"""
Copyright 2017-2024 SensiML Corporation

This file is part of SensiML™ Piccolo AI™.

SensiML Piccolo AI is free software: you can redistribute it and/or
modify it under the terms of the GNU Affero General Public License
as published by the Free Software Foundation, either version 3 of
the License, or (at your option) any later version.

SensiML Piccolo AI is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public
License along with SensiML Piccolo AI. If not, see <https://www.gnu.org/licenses/>.
"""

from django.utils.functional import cached_property


class DynamicFieldsMixin(object):
    @cached_property
    def fields(self):
        """
        Filters the fields according to the `fields` query parameter.
        Accepts query string array format only ?fields[]=model_results&fields[]=uuid&fields[]=name
        """
        fields = super(DynamicFieldsMixin, self).fields

        if not hasattr(self, "_context"):
            # We are being called before a request cycle
            return fields

        # Only filter if this is the root serializer, or if the parent is the
        # root serializer with many=True
        is_root = self.root == self
        parent_is_list_root = self.parent == self.root and getattr(
            self.parent, "many", False
        )
        if not (is_root or parent_is_list_root):
            return fields

        try:
            request = self.context["request"]
        except KeyError:
            return fields

        # parameters are found under the GET attribute.
        params = getattr(request, "query_params", getattr(request, "GET", None))

        try:
            filter_fields = params.getlist("fields[]")
        except AttributeError:
            filter_fields = None

        try:
            omit_fields = params.getlist("omit_fields[]")
        except AttributeError:
            omit_fields = []

        # Pass fields that are not specified in the `fields` argument.
        existing = set(fields.keys())
        if not filter_fields:
            # no fields param given, don't filter.
            allowed = existing
        else:
            allowed = set(filter(None, filter_fields))

        # omit fields in the `omit` argument.
        omitted = set(filter(None, omit_fields))

        for field in existing:

            if field not in allowed:
                fields.pop(field, None)

            if field in omitted:
                fields.pop(field, None)

        return fields
