#!/bin/bash
#   Copyright 2019 NEC Corporation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

BASEDIR=`dirname $0`

ALL_MANIFESTS="${BASEDIR}/epoch-install.yaml"
SOURCE_MANIFEST="${BASEDIR}/source"

cat <<EOF > ${ALL_MANIFESTS}
#   Copyright 2019 NEC Corporation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
EOF

echo    "#---- epochSystem.yaml"                >>   ${ALL_MANIFESTS}
cat     "${SOURCE_MANIFEST}/epochSystem.yaml"   >>   ${ALL_MANIFESTS}
echo    ""                                      >>   ${ALL_MANIFESTS}

echo    "#---- tektonNamespace.yaml"            >>   ${ALL_MANIFESTS}
echo    "---"                                   >>   ${ALL_MANIFESTS}
cat     "${SOURCE_MANIFEST}/tektonNamespace.yaml" >>   ${ALL_MANIFESTS}
echo    ""                                      >>   ${ALL_MANIFESTS}

for yamlfile in $( ls ${SOURCE_MANIFEST}/epoch*.yaml ); do
    if [ `basename "${yamlfile}"` != "epochSystem.yaml" ]; then
        echo    "#---- `basename ${yamlfile}`"  >>   ${ALL_MANIFESTS}
        echo    "---"                           >>   ${ALL_MANIFESTS}
        cat     ${yamlfile}                     >>   ${ALL_MANIFESTS}
        echo    ""                              >>   ${ALL_MANIFESTS}
    fi;
done;

for yamlfile in $( ls ${SOURCE_MANIFEST}/*.yaml | grep -v "^${SOURCE_MANIFEST}/epoch"); do
    if [ `basename "${yamlfile}"` != "tektonNamespace.yaml" ]; then
        echo    "#---- `basename ${yamlfile}`"  >>   ${ALL_MANIFESTS}
        echo    "---"                           >>   ${ALL_MANIFESTS}
        cat     ${yamlfile}                     >>   ${ALL_MANIFESTS}
        echo    ""                              >>   ${ALL_MANIFESTS}
    fi;
done;

