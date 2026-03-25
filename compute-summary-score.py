import utility

loop = [
    # ".data/source/device/db1/chunk=300-overlap=30",
    # ".data/source/device/db1/chunk=500-overlap=50",
    # ".data/source/device/db1/chunk=800-overlap=80",
    ".data/source/device/db1/chunk=1000-overlap=100",
    # ".data/source/device/db2/chunk=300-overlap=30",
    # ".data/source/device/db2/chunk=500-overlap=50",
    # ".data/source/device/db2/chunk=800-overlap=80",
    ".data/source/device/db2/chunk=1000-overlap=100",
    # ".data/source/device/db3/chunk=300-overlap=30",
    # ".data/source/device/db3/chunk=500-overlap=50",
    # ".data/source/device/db3/chunk=800-overlap=80",
    ".data/source/device/db3/chunk=1000-overlap=100"
]
for database in loop:
    schema = {
        'database': database,
        'exam': '.data/source/device/exam.json',
        'prompt': '.data/source/device/prompt.yaml',
        'model': 'qwen2.5:3b',
        'judge': 'llama3:8b'
    }
    evaluation = utility.Evaluation(schema)
    evaluation.readSummary()
    evaluation.writeScore()
    continue
