.. meta::
   :title: SensiML Python SDK - Proxy Setup
   :description: How to setup proxy information in the SensiML Python SDK

Proxy Setup
===========

If your company uses a proxy to connect to the internet you will need to set the proxy in order to access our servers. SensiML uses the default system proxy. If you want to set a specific proxy for this session, you need to set the proxy as an environmental variable in the notebook::

      import os
      os.environ['http_proxy']  = 'http-proxy-address'
      os.environ['https_proxy'] = 'https-proxy-address'