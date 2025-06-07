class OdooResponseUtils:

    @staticmethod
    def success(data=None, code=200, message=None):
        response = {
            'status': 'success',
            'code': code,
        }
        if data is not None:
            response['data'] = data
        if message is not None:
            response['message'] = message
        return response

    @staticmethod
    def error(error=None, code=400, error_details=None):
        response = {
            'status': 'error',
            'code': code,
        }
        if error is not None:
            response['error'] = error
        if error_details is not None:
            response['error_details'] = error_details
        return response