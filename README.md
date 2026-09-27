# hyemin-ai.github.io

- `/` → [만트라](https://hyemin-ai.github.io/Gangnam-beauty/prayer/) 앱으로 이동
- `/.well-known/assetlinks.json` → 구글 플레이 앱(`io.github.hyemin_ai.mantra`)이 이 사이트의 주인임을 증명하는 파일.
  이 파일이 있어야 앱 위쪽에 인터넷 주소창이 보이지 않는다.
  구글 플레이 '앱 서명 키'의 SHA-256 지문도 `sha256_cert_fingerprints` 목록에 함께 넣어야 한다.
- `.nojekyll` → 점(.)으로 시작하는 `.well-known` 폴더도 공개되도록 하는 설정
