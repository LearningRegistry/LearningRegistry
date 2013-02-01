# Author: Jim Klo jim.klo[at]sri[dot]com 
#
# LICENSE
# Copyright 2013 SRI International

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from datetime import datetime
from jsonschema import validate, Draft3Validator, ValidationError, validates, RefResolver
from urllib import urlopen
from lr.lib.uri_validate import URI
import re, iso8601, urlparse

class UnsupportedFormatError(Exception):
    """
    Valid Draft3 format however unsupported by this validator.
    """

class UnknownFormatError(ValidationError):
    """
    Unknown format error.
    """

@validates("draft3")
class LRDraft3Validator(Draft3Validator):
    ISO8601_DATE_TIME_REGEX = re.compile(r"^(?P<year>[0-9]{4})-(?P<month>[0-9]{1,2})-(?P<day>[0-9]{1,2})"
        r"(?P<separator>T)(?P<hour>[0-9]{2}):(?P<minute>[0-9]{2}):(?P<second>[0-9]{2})(?P<timezone>Z)$")

    ISO8601_DATE_REGEX = re.compile(r"^(?P<year>[0-9]{4})-(?P<month>[0-9]{1,2})-(?P<day>[0-9]{1,2})$")

    # URI regex from https://gist.github.com/138549/download
    URI_REGEX = re.compile("^%s$"%URI, re.X)

    def __init__(self, schema, types=(), resolver=None):
        if resolver is None:
            resolver = LRRefResolver.from_schema(schema)

        super(LRDraft3Validator, self).__init__(schema, types, resolver)

    def validate_format(self, format, instance, schema):

        def is_date(val):
            if self.is_type(val, "string"):
                m =  LRDraft3Validator.ISO8601_DATE_REGEX.match(val)
                if m:
                    groups = m.groupdict()
                    try:
                        datetime(int(groups["year"]), int(groups["month"]), int(groups["day"]), tzinfo=iso8601.iso8601.UTC)
                        return True
                    except ValueError:
                        pass
            return False


        def is_date_time(val):
            if self.is_type(val, "string"):
                m =  LRDraft3Validator.ISO8601_DATE_TIME_REGEX.match(val)
                if m:
                    groups = m.groupdict()
                    try:
                        datetime(int(groups["year"]), int(groups["month"]), int(groups["day"]),
                            int(groups["hour"]), int(groups["minute"]), int(groups["second"]),
                            tzinfo=iso8601.iso8601.UTC)
                        return True
                    except ValueError:
                        pass
            return False

        def is_utc_millisec(val):
            if self.is_type(val, "number") and val >= 0:
                return True
            return False


        def is_regex(val):
            if self.is_type(val, "string"):
                try:
                    exp = re.compile(val)
                    if exp:
                        return True
                except:
                    pass
            return False

        def is_uri(val):
            if self.is_type(val, "string"):
                if LRDraft3Validator.URI_REGEX.match(val) is not None:
                    # print "regex matched a uri: %r" % val
                    return True
                # else:
                #     try:
                #         print "didn't match"
                #         (first, sep, rest) = val.partition("#")
                #         urlopen(first).read()
                #         return True
                #     except:
                #         pass

            return False

        def unsupported(val):
            raise UnsupportedFormatError()
            return False

        formats = {
            "date-time": is_date_time,
            "date": is_date,
            "time": unsupported,
            "utc-millisec": is_utc_millisec,
            "regex": is_regex,
            "color": unsupported,
            "style": unsupported,
            "phone": unsupported,
            "uri": is_uri,
            "email": unsupported,
            "ip-address": unsupported,
            "ipv6": unsupported,
            "hostname": unsupported
        }

        try:
            if not formats[format](instance):
                yield ValidationError("%r is not formatted as a %r" % (instance, format)) 
        except UnsupportedFormatError as e:
            yield ValidationError("%r is an unsupported format" % format)
        except KeyError:
            if is_uri(format):
                yield ValidationError("custom format is unsupported")
            else:
                yield ValidationError("%r is an unknown format" % format)
        except GeneratorExit:
            raise StopIteration




LRDraft3Validator.META_SCHEMA = Draft3Validator.META_SCHEMA
LRDraft3Validator.META_SCHEMA["properties"]["format"].update(
    {
        "type": "string",
        "enum": ["date-time", "date", "utc-millisec", "regex", "uri"]
    }
)           

class LRRefResolver(RefResolver):
    def resolve(self, ref):
        """
        Resolve a JSON ``ref``.

        :argument str ref: reference to resolve
        :returns: the referrant document

        """

        base_uri = self.base_uri
        full_uri = urlparse.urljoin(base_uri, ref)
        uri, fragment = urlparse.urldefrag(full_uri)

        if not full_uri.startswith(uri) and re.match("^file:[^/].*", full_uri):
            uri = re.sub("([^:]+:)/+", "\\1", uri) 

        if uri in self.store:
            document = self.store[uri]
        elif not uri or uri == self.base_uri:
            document = self.referrer
        else:
            document = self.resolve_remote(uri)

        return self.resolve_fragment(document, fragment.lstrip("/"))



