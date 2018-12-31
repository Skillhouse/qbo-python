


from wsgiref.handlers import BaseHandler


def finish_response(self):
    try:
        if not self.result_is_file() or not self.sendfile():
            for data in self.result:
                if data:
                    self.write(data)
            self.finish_content()
    finally:
        self.close()


BaseHandler.finish_response = finish_response
