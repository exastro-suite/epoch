// Copyright 2019 NEC Corporation
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//

let langArray = {};
    langArray['EP000-0001'] = "オーナー";
    langArray['EP000-0002'] = "管理者";
    langArray['EP000-0003'] = "メンバー管理";
    langArray['EP000-0004'] = "CI設定";
    langArray['EP000-0005'] = "CI確認";
    langArray['EP000-0006'] = "CD設定";
    langArray['EP000-0007'] = "CD実行";
    langArray['EP000-0008'] = "CD確認";
    langArray['EP000-0009'] = "可能な操作";
    langArray['EP000-0010'] = "ワークスペース参照";
    langArray['EP000-0011'] = "ワークスペース更新（名称）";
    langArray['EP000-0012'] = "ワークスペース更新（CI）";
    langArray['EP000-0013'] = "ワークスペース更新（CD）";
    langArray['EP000-0014'] = "ワークスペース削除";
    langArray['EP000-0015'] = "オーナーロール設定";
    langArray['EP000-0016'] = "メンバー追加";
    langArray['EP000-0017'] = "ロール変更";
    langArray['EP000-0018'] = "CIパイプライン結果確認";
    langArray['EP000-0019'] = "Manifestテンプレート・パラメータ編集";
    langArray['EP000-0020'] = "CD実行";
    langArray['EP000-0021'] = "CD実行結果確認";
    langArray['EP010-0100'] = "ワークスペースの一覧です。";
    langArray['EP010-0101'] = "ワークスペース名";
    langArray['EP010-0102'] = "ロール";
    langArray['EP010-0103'] = "メンバー数";
    langArray['EP010-0104'] = "最終更新日時";
    langArray['EP010-0105'] = "備考";
    langArray['EP010-0106'] = "退去";
    langArray['EP010-0107'] = "ワークスペースから退去しました";
    langArray['EP010-0110'] = "[DONE] 退去";
    langArray['EP010-0111'] = "[FAIL] 退去";
    langArray['EP010-0200'] = "ワークスペース設定";
    langArray['EP010-0201'] = "Deploy権限";
    langArray['EP010-0202'] = "CD実行が可能なユーザ全員";
    langArray['EP010-0203'] = "以下で選択したユーザのみ";
    langArray['EP010-0204'] = "チェックボックス";
    langArray['EP010-0205'] = "名前";
    langArray['EP010-0206'] = "[DONE] CD実行ユーザ取得";
    langArray['EP010-0207'] = "[FAIL] CD実行ユーザ取得";
    langArray['EP010-0400'] = "のメンバー一覧";
    langArray['EP010-0401'] = "ユーザ名";
    langArray['EP010-0402'] = "名";
    langArray['EP010-0403'] = "姓";
    langArray['EP010-0404'] = "ロール";
    langArray['EP010-0405'] = "メンバー追加";
    langArray['EP010-0406'] = "ロール変更";
    langArray['EP010-0407'] = "メンバーの追加";
    langArray['EP010-0408'] = "ロール／ユーザー";
    langArray['EP010-0409'] = "ロール詳細";
    langArray['EP010-0410'] = "全解除";
    langArray['EP010-0411'] = "登録";
    langArray['EP010-0412'] = "キャンセル";
    langArray['EP010-0413'] = "閉じる";
    langArray['EP010-0414'] = "最低1人以上のオーナーは必要です";
    langArray['EP010-0415'] = "ロールを変更する権限がありません";
    langArray['EP010-0416'] = "ロールの変更がありません";
    langArray['EP010-0417'] = "オーナーを解除する権限がありません";
    langArray['EP010-0418'] = "メンバーが選択されていません";
    langArray['EP010-0419'] = "・ワークスペースの作成者\n ・ワークスペース操作の全権限を持つ";
    langArray['EP010-0420'] = "・ワークスペース削除以外の操作が可能な権限";
    langArray['EP010-0421'] = "・メンバーの追加・解除、ロール変更のみの操作が可能な権限";
    langArray['EP010-0422'] = "・アプリケーションの開発者用のアカウント\n ・CIパイプライン(ビルドパラメータ等)の変更が可能\n ・Manifestテンプレートのアップロードも可能";
    langArray['EP010-0423'] = "・アプリケーションの開発者用のアカウント\n ・CIパイプライン(ビルドパラメータ等)の変更は不可";
    langArray['EP010-0424'] = "・ワークスペースのCDパイプラインの設定値の変更が可能\n ・Manifestパラメータの編集も可能";
    langArray['EP010-0425'] = "・CD実行可能なロール\n ・CD実行の結果の参照も可能";
    langArray['EP010-0426'] = "・CD実行の結果のみ参照可能なロール\n ・CD実行時のトラブル解析用に特化したロール";
    