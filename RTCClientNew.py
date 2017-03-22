import requests
from urllib import urlencode

class RTCClientNew:

    CONTENT_XML = "text/xml"
    CONTENT_URL_ENCODED = "application/x-www-form-urlencoded"
    OSLC_CR_XML = "application/x-oslc-cm-change-request+xml"
    OSLC_CR_JSON = "application/x-oslc-cm-change-request+json"
    
    def __init__(self, url, username, password, resource_url, first):
        if (first):
            self.resource_url = resource_url
            self.username = username
            self.password = password
            self.url = url
            self.headers = self._get_headers()
        
        resp = self.get(resource_url,
                verify=False,
                headers=self.headers)
        self.query = resp.content

    def getQuery(self):
        return self.query

    def get(self, url,
            verify=False, headers=None,
            timeout=60, **kwargs):
        if (headers == None):
            headers=self.headers

        print "Get response from " + url
        response = requests.get(url, verify=verify, headers=headers,
                                timeout=timeout, **kwargs)
        if response.status_code != 200:
            print response
            print 'Failed GET request at  with response: ' + response.content
            #response.raise_for_status()
        return response

    def _get_headers(self):
        _allow_redirects = False
        _headers = {"Content-type": "text/xml", "Accept": "text/xml"}
        session =requests.session()
        
        resp = self.get(self.url + "/authenticated/identity",
                        verify=False,
                        headers=_headers,
                        allow_redirects=_allow_redirects
                        )
        
        _headers["Content-type"] = self.CONTENT_URL_ENCODED
        _headers["Cookie"] = resp.headers.get("set-cookie")

        credentials = urlencode({"j_username": self.username,
                                 "j_password": self.password})
        
        resp = self.post(self.url + "/authenticated/j_security_check",
                         data=credentials,
                         verify=False,
                         headers=_headers,
                         allow_redirects=_allow_redirects)
        
        authfailed = resp.headers.get("x-com-ibm-team-repository-web-auth-msg")
        if authfailed == "authfailed":
            return False


        _headers["Cookie"] = resp.headers.get("set-cookie")

        resp = self.get(self.url + "/authenticated/identity",
                        verify=False,
                        headers=_headers,
                        allow_redirects=_allow_redirects)
        
        _headers["Cookie"] += "; " + resp.headers.get("set-cookie")
        _headers["Accept"] = self.CONTENT_XML
        return _headers
    
    def post(self, url, data=None, json=None,
             verify=False, headers=None, timeout=60, **kwargs):
        response = requests.post(url, data=data, json=json,
                                 verify=verify, headers=headers,
                                 timeout=timeout, **kwargs)

        if response.status_code not in [200, 201]:
            print 'Failed POST request at  with response: ' + response.content
        return response
