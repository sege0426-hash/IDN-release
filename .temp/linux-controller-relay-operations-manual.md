# IDN 컨트롤러 / 중계서버 운영 메뉴얼

## 1. 목적

이 문서는 Linux 환경에서 IDN 컨트롤러와 중계서버를 설치하고 운영하는 실제 절차를 정리한 문서다.

이번 패키지의 목표는 두 가지다.

- 사용자는 설치 시 `./install.sh`만 실행한다.
- 설치가 끝난 뒤에는 컨트롤러 ID 또는 중계서버 ID만 입력해서 로그인한다.

별도의 패키지 설치 명령, auth 서버 수동 설정 명령, NIC 수동 설정 명령은 일반 사용자 절차에서 제외한다.

## 2. 기본 동작 방식

패키지에는 기본 auth 서버 정보가 별도 파일로 포함되어 있다.

- 오케스트레이터 주소: `61.109.220.75`
- auth 포트: `15004`

설치 스크립트는 이 정보를 자동으로 아래 파일에 배치한다.

- 컨트롤러: `/etc/default/idn-controller.auth`
- 중계서버: `/etc/default/idn-edge.auth`

사용자는 이 파일을 직접 수정할 필요가 없다.

## 3. 배포 파일

### 3.1 컨트롤러 패키지

- `idn-controller-YYYYMMDD.tar.gz`

### 3.2 중계서버 패키지

- `idn-relay-YYYYMMDD.tar.gz`

## 4. 설치 절차

### 4.1 컨트롤러

패키지를 서버에 복사한 뒤 아래처럼 압축을 해제한다.

```bash
mkdir -p ~/idn-controller-package
tar xzf idn-controller-YYYYMMDD.tar.gz -C ~/idn-controller-package
cd ~/idn-controller-package
```

설치 디렉터리에서 아래만 실행한다.

```bash
./install.sh
```

설치가 끝나면 아래 파일이 자동으로 배치된다.

- 실행 파일: `/opt/idn/controller/bin/idn-controllerd`
- 실행 래퍼: `/usr/local/bin/idn-controller`
- 서비스 파일: `/etc/systemd/system/idn-controller.service`
- auth 설정: `/etc/default/idn-controller.auth`
- ID 저장 파일: `/etc/default/idn-controller`

### 4.2 중계서버

패키지를 서버에 복사한 뒤 아래처럼 압축을 해제한다.

```bash
mkdir -p ~/idn-relay-package
tar xzf idn-relay-YYYYMMDD.tar.gz -C ~/idn-relay-package
cd ~/idn-relay-package
```

설치 디렉터리에서 아래만 실행한다.

```bash
./install.sh
```

설치가 끝나면 아래 파일이 자동으로 배치된다.

- 실행 파일: `/opt/idn/relay/bin/idn-edged`
- 실행 래퍼: `/usr/local/bin/idn-relay`
- 서비스 파일: `/etc/systemd/system/idn-relay.service`
- auth 설정: `/etc/default/idn-edge.auth`
- ID 저장 파일: `/etc/default/idn-relay`

추가로 중계서버가 필요한 런타임 디렉터리도 자동 생성된다.

## 5. 로그인 및 서비스 시작

### 5.1 컨트롤러

설치 후 아래 명령만 실행한다.

```bash
idn-controller
```

프롬프트가 뜨면 컨트롤러 ID만 입력한다.

```text
Controller ID: test03
```

입력이 끝나면 래퍼가 자동으로 다음을 처리한다.

1. ID를 `/etc/default/idn-controller`에 저장
2. `idn-controller.service` 활성화
3. 서비스 재시작

인자를 직접 주는 방식도 가능하다.

```bash
idn-controller test03
```

### 5.2 중계서버

설치 후 아래 명령만 실행한다.

```bash
idn-relay
```

프롬프트가 뜨면 중계서버 ID만 입력한다.

```text
Relay ID: test03_relay
```

입력이 끝나면 래퍼가 자동으로 다음을 처리한다.

1. ID를 `/etc/default/idn-relay`에 저장
2. `idn-relay.service` 활성화
3. 서비스 재시작

인자를 직접 주는 방식도 가능하다.

```bash
idn-relay test03_relay
```

## 6. 상태 확인 명령

### 6.1 컨트롤러

```bash
idn-controller status
idn-controller logs
sudo idn-controller restart
sudo idn-controller stop
```

### 6.2 중계서버

```bash
idn-relay status
idn-relay logs
sudo idn-relay restart
sudo idn-relay stop
```

## 7. 재부팅 이후 동작

한 번 로그인해서 ID가 저장되면, 이후 재부팅 시 systemd가 같은 ID로 자동 기동한다.

즉 일반 사용자는 최초 1회만 ID를 입력하면 된다.

## 8. 업데이트 절차

업데이트도 새 패키지를 압축 해제한 뒤 설치 디렉터리에서 아래만 실행하면 된다.

### 8.1 컨트롤러

```bash
mkdir -p ~/idn-controller-package
tar xzf idn-controller-YYYYMMDD.tar.gz -C ~/idn-controller-package
cd ~/idn-controller-package
./install.sh
```

### 8.2 중계서버

```bash
mkdir -p ~/idn-relay-package
tar xzf idn-relay-YYYYMMDD.tar.gz -C ~/idn-relay-package
cd ~/idn-relay-package
./install.sh
```

기존 auth 설정과 저장된 ID가 이미 존재하면 유지된다.

## 9. 제거 절차

### 9.1 컨트롤러

```bash
./uninstall.sh
```

### 9.2 중계서버

```bash
./uninstall.sh
```

기본값으로는 auth 설정과 ID 파일은 유지된다.

## 10. 운영자 참고사항

- 일반 사용자에게는 `./install.sh`와 `idn-controller` 또는 `idn-relay`만 안내하면 된다.
- 오케스트레이터 주소가 바뀌는 경우에만 아래 파일을 운영자가 수정하면 된다.
  - `/etc/default/idn-controller.auth`
  - `/etc/default/idn-edge.auth`
- 현재 검증 기준 오케스트레이터는 `61.109.220.75:15004`, 제어 포트는 `15005`다.
