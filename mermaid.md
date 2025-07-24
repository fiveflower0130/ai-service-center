graph TD
    subgraph "使用者端"
        Client[外部系統 / 前端]
    end

    subgraph "AI Services Center (FastAPI 應用)"
        Client -- "1. HTTP POST /drill_map/classify" --> API_Layer
        
        subgraph "API 層 (app/api)"
            API_Layer("FastAPI Router\n[app/api/drill_map.py](app/api/drill_map.py)")
        end

        subgraph "AI 模組層 (app/ai_modules)"
            AI_Module("DrillMapAIModule\n[app/ai_modules/drill_map_ai/module.py](app/ai_modules/drill_map_ai/module.py)")
            AI_Module_Others["其他 AI 模組\n(未來擴展)"]
        end

        subgraph "資料存取層 (app/crud, app/models)"
            CRUD_Layer("CRUD 操作\n[app/crud/drill_map.py](app/crud/drill_map.py)")
            ORM_Models("ORM 模型\n[app/models/mysql_model.py](app/models/mysql_model.py)")
        end

        subgraph "核心服務"
            Response_Helper("回應處理\n[app/utils/response_helper.py](app/utils/response_helper.py)")
            Schema_Validator("資料驗證\n[app/schemas.py](app/schemas.py)")
        end

        subgraph "資料庫"
            MySQL_DB[("MySQL Database\n[app/database/mysql_database.py](app/database/mysql_database.py)")]
        end

        API_Layer -- "2. 呼叫 AI 函式" --> AI_Module
        AI_Module -- "3. 執行 OCR/圖像/表格預測" --> AI_Module
        API_Layer -- "4. 呼叫 CRUD 儲存" --> CRUD_Layer
        CRUD_Layer -- "5. 使用 ORM 模型" --> ORM_Models
        ORM_Models -- "6. 寫入資料庫" --> MySQL_DB
        API_Layer -- "7. 使用回應處理" --> Response_Helper
        API_Layer -- "8. 資料驗證" --> Schema_Validator
        Response_Helper -- "9. 回傳 JSON 結果" --> Client
    end

    style Client fill:#f9f,stroke:#333,stroke-width:2px
    style MySQL_DB fill:#bbf,stroke:#333,stroke-width:2px
    style AI_Module fill:#9ff,stroke:#333,stroke-width:2px
    style AI_Module_Others fill:#ddd,stroke:#333,stroke-width:1px,stroke-dasharray: 5 5
