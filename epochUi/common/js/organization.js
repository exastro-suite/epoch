/*
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
*/

function get_organization() {
  return [
    {"organization_name": "sample 1"},
    {"organization_name": "sample 2"},
    {"organization_name": "sample 3"},
    {"organization_name": "sample 4"}
  ];
}

function generate_organization_elements() {

  console.log('generate_organization_elements');
  var organization_data = get_organization();
  console.log(organization_data);

  organization_data.forEach(function(data) {
    var $dummy_row = $('#dummy-row');
    var $tbody = $dummy_row.closest('tbody');

    var $new_row = $dummy_row.clone(true);
    $new_row.find('A').text(data.organization_name);
    $new_row.removeAttr('hidden');
    $tbody.append($new_row);
  });
}

function create_organization() {

  var form = document.forms['organization-data'];
  var add_info_key = []
  form.elements['add_info_key'].forEach(function(elem) {
    add_info_key.push(elem.value);
  });
  var add_info_value = []
  form.elements['add_info_value'].forEach(function(elem) {
    add_info_value.push(elem.value);
  });
  var param = {
    'organization_name': form.elements['organization_name'].value,
    'add_info_key': add_info_key,
    'add_info_value': add_info_value
  }
  console.log(JSON.stringify(param)); 

  new Promise((resolve, reject) => {

    $.ajax({
      "type": "POST",
      "url": organization_api_conf.api.resource.post
    }).done(function(data) {
      console.log("DONE : オーガナイゼーション登録");
      console.log(typeof(data));
      console.log(JSON.stringify(data));

      resolve();
    }).fail(function() {
      console.log("FAIL : オーガナイゼーション登録");
      // 失敗
      reject();
    });

  }).then(() => {
    console.log('Complete !!');
    window.location.href = "organization-list.html";
  }).catch(() => {
    alert("オーガナイゼーション登録に失敗しました");
    console.log('Fail !!');
  });
}


$(function(){
  $('#apply-workspace-button').click(()=>{
    create_organization();
  });

  generate_organization_elements();
});
