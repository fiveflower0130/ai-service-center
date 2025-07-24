# AI Services Center

This platform will serve as the central hub for managing and deploying all future AI prediction services.


## docker container啟動方式
1. 確保已安裝 Docker 和 Docker Compose。
2. 在終端機中，切換到此專案的根目錄。
3. 執行以下命令以啟動服務：
   ```bash
   docker-compose up -d
   ```
4. 等待服務啟動完成後，您可以通過瀏覽器連結 `http://localhost:8009` 來查看服務狀態。

## 停止服務
要停止服務，請在終端機中執行以下命令：
```bash
docker-compose down
```
## uv手動動啟動方式
1. 在終端機中，進入到此專案的根目錄。
2. 確保已安裝 Python >=3.10.13 或更高版本。
    ```bash
    uv python list --only-installed
    # 如果沒有安裝，請安裝python  
    uv python install 3.10.13
    # 指定版本
    uv python pin 3.10.13
    # 創建虛擬環境並啟動它：
    uv venv --python=3.10.13 # 預設會命名為".venv"
    # 安裝所需的 Python 套件：
    uv pip install -r requirements.txt
    # 啟動 uvicorn 伺服器：
    uv run ./main.py
   ```