import pandas as pd

# 读取文件1和文件2
file1 = pd.read_csv(r'data\fingerprint\chunk_for_test.csv', header=0)
file2 = pd.read_csv(r'data\fingerprint\yt_fp_for_test.csv', header=0)

# 打印列名，确认列名是否正确读取
print("File1 Columns:", file1.columns)
print("File2 Columns:", file2.columns)

# 定义要替换的URL ID范围 00000000000 到 00000000299
new_ids = [f'{i:011d}' for i in range(300)]  # 0 到 299 的11位数

# 遍历第一个文件的每一行
for idx, new_id in enumerate(new_ids):
    # 获取file1的URL（第一列）
    old_url = file1.iloc[idx, 0]  # 因为第一行是表头，所以从第二行开始
    
    # 提取旧的11位ID
    old_id = old_url[-11:]
    
    # 替换第一个文件中的URL
    file1.iloc[idx, 0] = old_url.replace(old_id, new_id)
    
    # 在第二个文件中找到并替换相应的URL（第二列）
    file2['url'] = file2['url'].apply(lambda x: x.replace(old_id, new_id) if old_id in x else x)
    
    # 更新第二个文件的ID列，保持与替换后的url一致
    file2.loc[file2['url'].str.contains(new_id), 'ID'] = idx

# 保存新的文件，保留表头
file1.to_csv('new_file1.csv', index=False)
file2.to_csv('new_file2.csv', index=False)

print("文件处理完成，已生成 new_file1.csv 和 new_file2.csv")