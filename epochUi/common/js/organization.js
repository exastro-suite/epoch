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

  // $.ajax({
  //   "type": "GET",
  //   "url": organization_api_conf.api.resource.get_all
  // }).done(function(data) {
  //   console.log("DONE : オーガナイゼーション一覧取得");
  //   console.log(typeof(data));
  //   console.log(JSON.stringify(data));

  //   return data;

  // }).fail(function() {
  //   // 失敗
  //   console.log("FAIL : オーガナイゼーション一覧取得");

  // });
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
  var additional_information = [];
  for(var i = 0; i < 5; i++) {
    var item = {};
    item[form.elements['add_info_key'][i]] = form.elements['add_info_value'][i];
    additional_information.push(item);
  }
  var param = {
    'organization_name': form.elements['organization_name'].value,
    'additional_information': JSON.stringify(additional_information)
  }
  console.log(JSON.stringify(param));

  $.ajax({
    "type": "POST",
    "url": organization_api_conf.api.resource.post,
    "data": param
  }).done(function(data) {
    console.log("DONE : オーガナイゼーション登録");
    console.log(typeof(data));
    console.log(JSON.stringify(data));

    window.location.href = "organization-list.html";

  }).fail(function() {
    // 失敗
    console.log("FAIL : オーガナイゼーション登録");

  });
}


$(function(){
  $('#apply-workspace-button').click(()=>{
    create_organization();
  });

  generate_organization_elements();
});
