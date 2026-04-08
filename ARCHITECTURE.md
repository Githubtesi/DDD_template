# ドメイン選定・実装ガイドライン
## 1. 参照資料
ドメインモデルの検討および実装にあたっては、以下のドキュメントを「ガードレール」として最優先で参照すること。 

必須資料: Domain Seedwork 復習ガイド (1).pdf

## 2. シードワーク選定フロー
AIは、検討対象の要素が以下のどの「部品」に該当するかを判断し、選定理由を提示してください。

## 3. 対話プロトコル
| 部品名 | 役割・特徴 | ファイルパス (`src/seedwork/domain/`) | ベースクラス名 |
| :--- | :--- |:--------------------------------| :--- |
| **Exceptions** | ルール違反を知らせるための独自エラー  | `domain_exception.py`           | `ValueObjectValidationError`, `DomainException` |
| **Value Object** | 中身が同じなら同じものとして扱う、不変のデータ | `value_object.py`               | `ValueObject`  |
| **Entity** | ID（背番号）で区別され、状態が変わっても同一性を保つもの  | `entity.py`                     | `Entity`  |
| **Aggregate Root** | 関連するデータの集まり（チーム）のキャプテンであり、外部との窓口  | `aggregate_root.py`             | `AggregateRoot`  |
| **Repository** | データの保存や取り出しを行う際の「お願いの仕方」を定めた窓口  | `repository.py`               | `Repository`  |
| **Domain Event** | ドメイン内で発生した「重要な出来事」を知らせるためのお手紙  | `domain_event.py`               | `DomainEvent`  |
| **Domain Service** | 特定のEntityに任せるのが不自然な、審判のような計算や判断  | `domain_service.py`                   | `DomainService`  |
| **Specification** | あるデータが合格基準を満たしているか判定するチェックリスト  | `specification.py`             | `Specification`  |
| **Factory** | 複雑なEntityやAggregateを正しい初期状態で組み立てる専門の工場  | `factory.py`                  | `Factory`  |
| **Policy** | 状況に応じて取り替え可能なビジネス上の「作戦」や計算の方針  | `domain_policy.py`                   | `DomainPolicy`  |
| **Events** | 情報を発信する人（Publisher）と受け取って動く人（Subscriber）の仕組み  | `domain_event.py`                     | `Publisher`, `Subscriber`  |


### 実装上の重要注意点
* [cite_start]**アプリケーションサービス:** * アプリケーションサービスはビジネスを動かす「手順」を記述するものです [cite: 56]。
    * [cite_start]ドメイン層ではなく、「アプリケーション層」に配置する必要があります [cite: 54, 57]。
* [cite_start]**Value Objectの特性:** * 一度決めたら内容を変えず、新しく作り直す「不変性」を持たせてください [cite: 13]。
    * [cite_start]データ作成時に自ら

### ステップ1：「〇〇に関するドメインを検討してください」への対応
1. Domain Seedwork 復習ガイド (1).pdf を読み込み、各部品の定義を再確認する。
2. 対象ドメインを分析し、どの概念を Entity, Value Object, Policy 等にするべきか提案する。
3. 提案時の必須項目:
 + 選定したシードワーク名とその理由。
 + そのモデルが守るべき具体的なルール（例：「金額はマイナスを許容しない」等）。

### ステップ2：「提案内容を元にドメインを作成してください」への対応
1. ステップ1で合意した構成に基づき、src/seedwork/ のベースクラスを継承して実装する。

2. 実装の共通ルール:
+ エラー処理: ルール違反時は exceptions.py の ValueObjectValidationError 等を利用する。 
+ カプセル化: Value Objectは不変とし、Entityの状態変更はメソッド経由で行う。 
+ 配置: application_service.py はドメイン層ではなく、**「アプリケーション層」**に置くことを厳守する。 