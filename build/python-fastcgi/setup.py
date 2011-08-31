#from distutils.core import setup, Extension
from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, Extension


c_ext = Extension("fcgi", ["fastcgi/pyfcgi.c"], libraries=["fcgi"],
                  include_dirs=["/usr/local/include"],
                  library_dirs=["/usr/local/lib"],
                  #extra_link_args=["-s"],
                 )

setup(name="python-fastcgi",
      version="1.1",
      description="Python wrapper for the Open Market FastCGI library",
      long_description="python-fastcgi is a lightweight wrapper around the Open Market FastCGI C Library/SDK. It includes threaded and forking WSGI 1.0 server implementations.",
      author="Cody Pisto",
      author_email="cody@hpcs.com",
      license="MIT-style",
      download_url="http://nebula.hpcs.com/python-fastcgi-1.1.tar.gz",
      platforms=["Posix", "MacOS X", "Windows"],
      classifiers=["Development Status :: 5 - Production/Stable",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: MIT License",
                   "Programming Language :: Python",
                   "Programming Language :: C",
                   "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries",
                   "Topic :: Software Development :: Libraries :: Python Modules"],
      packages=["fastcgi"],
      #data_files=[("share/doc/python-fastcgi/example", ["example/test.fcgi"])],
      ext_package='fastcgi',
      ext_modules=[c_ext],
      zip_safe=False,
     ) 
