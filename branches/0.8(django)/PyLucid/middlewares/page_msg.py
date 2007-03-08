
"""
Put the page_msg in the page

replace the tag and put a fieldset with the page messages in the cms page.
"""

TAG = "<lucidTag:page_msg/>"

FMT = (
    '\n<fieldset id="page_msg"><legend>page message</legend>\n'
    '%s'
    '\n</fieldset>'
)

class PageMessage(object):
    
    def process_response(self, request, response):
        try:
            page_msg = request.page_msg.get_page_msg()
        except AttributeError:
            # no page_msg object available (install section)
            return response
        
        if page_msg == "":
            # There is no messages to display ;)
            return response
        
        if TAG in response.content:
            response.content = response.content.replace(TAG, page_msg)
        else:
            response.content += page_msg

        return response
