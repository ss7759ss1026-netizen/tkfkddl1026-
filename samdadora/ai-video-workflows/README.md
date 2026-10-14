SAMDADORA AI VIDEO PRODUCTION v1.0

프로젝트 목적

SAMDADORA의 AI 오리지널 음악에 사용할 YouTube 플레이리스트 영상과 Shorts를 제작하고 관리합니다.

제작 과정

1. Suno 오리지널 음악 제작 및 Good Take Lock
2. Qwen 기반 이미지 생성 및 편집
3. LTX 2.5 / MiniMax H3 영상 제작
4. 영상 배경 수정 및 보정
5. 음악과 영상 합성
6. 16:9 YouTube 본편 및 9:16 Shorts 제작
7. 영상 품질 검수 후 발매

워크플로우 분류

- 01_Image_Generation: Qwen 이미지 생성
- 02_Image_to_Video: QwenEdit → LTX 2.5
- 03_MiniMax_Video_Transformation: MiniMax H3 영상 변환
- 04_Video_Editing_and_Animation: LTX 편집 및 AnimateDiff
- 05_Guides: 한국어 설명서와 사용 안내

원본 보존 원칙

- 기존 JSON 파일은 수정하지 않습니다.
- 기존 GitHub main 브랜치는 직접 변경하지 않습니다.
- 신규 파일은 별도 브랜치에서 관리합니다.
- 검증되지 않은 모델 및 노드는 UNKNOWN으로 표시합니다.
- Pull Request는 검수 후 병합합니다.

현재 상태

STATUS: PREPARATION

원본 JSON 10개는 별도 업로드 예정입니다.
ComfyUI 실제 실행 테스트는 아직 완료되지 않았습니다.
