from rest_framework.response import Response

from utils import storagers
from utils.oss import HarborObject
from . import exceptions
from .harbor import HarborManager
from .views import check_authenticated_or_bucket_token


def response_exception(exc: exceptions.Error):
    if not isinstance(exc, exceptions.Error):
        exc = exceptions.Error.from_error(exc)

    return Response(data=exc.err_data(), status=exc.status_code)


class V2ObjectHandler:
    @staticmethod
    def post_part(view, request, kwargs):
        """
        上传一个分片
        """
        objpath = kwargs.get(view.lookup_field, '')
        bucket_name = kwargs.get('bucket_name', '')

        try:
            validate_data = V2ObjectHandler.post_part_validate(request)
        except exceptions.Error as exc:
            return response_exception(exc)

        content_md5 = validate_data['content_md5']
        content_length = validate_data['content_length']
        offset = validate_data['offset']
        reset = validate_data['reset']

        try:
            check_authenticated_or_bucket_token(request, bucket_name=bucket_name, act='write', view=view)
        except exceptions.Error as exc:
            return response_exception(exc)

        try:
            post_data = request.data
        except Exception as e:
            exc = exceptions.Error()
            return response_exception(exc)

        file = post_data.get('file')
        if not file:
            return response_exception(
                exc=exceptions.BadRequest(message='Request body is empty.'))

        if content_length != file.size:
            return response_exception(
                exc=exceptions.BadRequest(
                    message='The length of body not same header "Content-Length"'))

        if content_md5 != file.file_md5:
            return response_exception(
                exc=exceptions.BadDigest())

        hmanager = HarborManager()
        try:
            created = hmanager.write_file(bucket_name=bucket_name, obj_path=objpath, offset=offset, file=file,
                                          reset=reset, user=request.user)
        except exceptions.HarborError as exc:
            return response_exception(exc)

        return Response(data={'created': created}, status=200)

    @staticmethod
    def post_part_validate(request):
        """
        :return:
            {
                'content_md5': str,
                'content_length': int,
                'offset': int,
                'reset': bool
            }
        :raises: Error
        """
        content_md5 = request.headers.get('Content-MD5', '').lower()
        if not content_md5:
            raise exceptions.InvalidDigest()

        offset = request.query_params.get('offset')
        if not offset:
            raise exceptions.BadRequest(message='Param "offset" is required')

        try:
            offset = int(offset)
            if offset < 0:
                raise ValueError
        except (ValueError, TypeError):
            raise exceptions.BadRequest(message='Param "offset" is invalid')

        content_length = request.headers.get('content-length')
        if not content_length:
            raise exceptions.BadRequest(
                message='header "Content-Length" is required')

        try:
            content_length = int(content_length)
        except (ValueError, TypeError):
            raise exceptions.BadRequest(
                message='header "Content-Length" is invalid')

        reset = request.query_params.get('reset', '').lower()
        if reset == 'true':
            reset = True
        else:
            reset = False

        return {
            'content_md5': content_md5,
            'content_length': content_length,
            'offset': offset,
            'reset': reset
        }

    @staticmethod
    def put_object(view, request, kwargs):
        objpath = kwargs.get(view.lookup_field, '')
        bucket_name = kwargs.get('bucket_name', '')

        content_md5 = view.request.headers.get('Content-MD5', '')
        if not content_md5:
            return response_exception(exc=exceptions.InvalidDigest())

        content_length = request.headers.get('content-length')
        if not content_length:
            return response_exception(
                exc=exceptions.BadRequest(
                    message='header "Content-Length" is required'))

        try:
            check_authenticated_or_bucket_token(request, bucket_name=bucket_name, act='write', view=view)
        except exceptions.Error as exc:
            return response_exception(exc)

        hmanager = HarborManager()
        try:
            bucket, obj, created = hmanager.create_empty_obj(
                bucket_name=bucket_name, obj_path=objpath, user=request.user)
        except exceptions.HarborError as exc:
            return response_exception(exc)

        pool_name = bucket.get_pool_name()
        obj_key = obj.get_obj_key(bucket.id)

        rados = HarborObject(pool_name=pool_name, obj_id=obj_key, obj_size=obj.si)
        if created is False:  # 对象已存在，不是新建的
            try:
                hmanager._pre_reset_upload(obj=obj, rados=rados)  # 重置对象大小
            except Exception as e:
                return response_exception(
                    exc=exceptions.Error(message=f'reset object error, {str(e)}'))

        return V2ObjectHandler.update_handle(view=view, request=request, bucket=bucket,
                                             obj=obj, rados=rados, created=created)

    @staticmethod
    def update_handle(view, request, bucket, obj, rados, created):
        pool_name = bucket.get_pool_name()
        obj_key = obj.get_obj_key(bucket.id)
        uploader = storagers.FileUploadToCephHandler(request, pool_name=pool_name, obj_key=obj_key)
        request.upload_handlers = [uploader]

        def clean_put(_uploader, _obj, _created, _rados):
            # 删除数据和元数据
            f = getattr(_uploader, 'file', None)
            s = f.size if f else 0
            _rados.delete(obj_size=s)
            if _created:
                _obj.delete()

        # 数据验证
        try:
            put_data = request.data
        except Exception as e:
            clean_put(uploader, obj, created, rados)
            return response_exception(exc=exceptions.Error(message=str(e)))

        file = put_data.get('file')
        if not file:
            return response_exception(
                exc=exceptions.BadRequest('Request body is empty.'))

        content_md5 = view.request.headers.get('Content-MD5', '').lower()
        if content_md5 != file.file_md5.lower():
            # 删除数据和元数据
            clean_put(uploader, obj, created, rados)
            return response_exception(exceptions.BadDigest())

        try:
            obj.si = file.size
            obj.md5 = content_md5
            obj.save(update_fields=['si', 'md5'])
        except Exception as e:
            # 删除数据和元数据
            clean_put(uploader, obj, created, rados)
            exc = exceptions.Error(message=str(e))
            return response_exception(exc)

        return Response(data={'created': created})

