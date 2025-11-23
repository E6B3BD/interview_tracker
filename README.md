### interview_tracker【面试追踪】

##### 配置项目

拉取代码

```
https://github.com/E6B3BD/interview_tracker.git
cd interview_tracker
```

pip环境

```
pip install -r requirements.txt
```

数据库

```
/interview_tracker/db/interview_system.sql
```

models.py

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',          
    'database': 'interview_system',
    'charset': 'utf8mb4'
}
```

运行

```
python app.py
```

##### 注意事项

只有root权限账户才有删除功能，自己创建root账户