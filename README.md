# IDN Manual Web

IDN 사용자 매뉴얼을 정적 웹 페이지로 관리하기 위한 프로젝트다.

## 구조

- `index.html`
  - 매뉴얼 목록과 진입 페이지
- `manuals/super-admin.html`
  - 최고 관리자 매뉴얼 본문
- `assets/css/`
  - 공통 스타일, 레이아웃, 컴포넌트, 매뉴얼 전용 스타일
- `assets/js/`
  - 공통 내비게이션, 목차 활성화 스크립트

## 유지보수 방식

1. 본문 수정
   - `manuals/super-admin.html`에서 각 `section` 내부 내용을 직접 수정
   - 새 문서를 만들 때는 해당 파일을 복사해 `group-admin.html`, `user.html`처럼 추가

2. 공통 스타일 수정
   - 색상/타이포: `assets/css/tokens.css`
   - 레이아웃: `assets/css/layout.css`
   - 표/배지/카드: `assets/css/components.css`
   - 문서 본문: `assets/css/manual.css`

3. 공통 동작 수정
   - 좌측 목차 활성화: `assets/js/toc.js`
   - 모바일 메뉴 토글: `assets/js/navigation.js`

## 실행 방법

- 파일 탐색기에서 `index.html`을 열면 된다.
- 별도 빌드 도구는 없다.

## 권장 작성 규칙

- 각 문단 블록은 `manual-section` 단위로 유지
- 목차 링크 대상은 `id` 속성과 동일하게 관리
- 표는 `doc-table`
- 스크린샷 삽입 표는 `doc-table screenshot-table`

