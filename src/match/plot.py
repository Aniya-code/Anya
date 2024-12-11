# plot.py
import matplotlib.pyplot as plt
import seaborn as sns
import re
import os
import configparser

config = configparser.ConfigParser()
config.read('src/match/config.ini')
PIC_DIR = config.get('OUTPUT', 'PIC_DIR')
BOX_DIFF_PIC = config.get('IMAGES', 'BOX_DIFF_PIC')
BAR_XY_PAIR_PIC = config.get('IMAGES', 'BAR_XY_PAIR_PIC')
PIE_XY_PAIR_PIC = config.get('IMAGES', 'PIE_XY_PAIR_PIC')
BAR_ITAG_PAIR_PIC = config.get('IMAGES', 'BAR_ITAG_PAIR_PIC')
PIE_ITAG_PAIR_PIC = config.get('IMAGES', 'PIE_ITAG_PAIR_PIC')
BAR_CHUNK_NUM_PIC = config.get('IMAGES', 'BAR_CHUNK_NUM_PIC')
PIE_CHUNK_NUM_PIC = config.get('IMAGES', 'PIE_CHUNK_NUM_PIC')
BAR_TIME_NUM_PIC = config.get('IMAGES', 'BAR_TIME_NUM_PIC')
PIE_TIME_NUM_PIC = config.get('IMAGES', 'PIE_TIME_NUM_PIC')


class DataPlotter:
    def __init__(self, diff_distribution, xy_pair_count, itag_pair_count, chunk_num, time_num):
        # self.diff_distribution = diff_distribution
        # self.xy_pair_count = xy_pair_count
        # self.itag_pair_count = itag_pair_count
        # self.chunk_num = chunk_num
        self.sorted_diff_distribution = dict(sorted(diff_distribution.items(), key=lambda item: self.get_key(item[0])))
        self.sorted_xy_pair_count = dict(sorted(xy_pair_count.items(), key=lambda item: self.get_key(item[0])))
        
        if not os.path.exists(PIC_DIR):
            os.makedirs(PIC_DIR)
        
        self.plot_box(self.sorted_diff_distribution, os.path.join(PIC_DIR, BOX_DIFF_PIC), 'Chunk-body error distribution')
        self.plot_bar(self.sorted_xy_pair_count, os.path.join(PIC_DIR, BAR_XY_PAIR_PIC), 'The number of occurrences of each xVyA combination')
        self.plot_pie(self.sorted_xy_pair_count, os.path.join(PIC_DIR, PIE_XY_PAIR_PIC), 'The number of occurrences of each xVyA combination')
        self.plot_bar(itag_pair_count, os.path.join(PIC_DIR, BAR_ITAG_PAIR_PIC), 'The number of occurrences of each V:itag/A:itag combination')
        self.plot_pie(itag_pair_count, os.path.join(PIC_DIR, PIE_ITAG_PAIR_PIC), 'The number of occurrences of each V:itag/A:itag combination')
        self.plot_bar(chunk_num, os.path.join(PIC_DIR, BAR_CHUNK_NUM_PIC), 'Number of chunks required for successful matching')
        self.plot_pie(chunk_num, os.path.join(PIC_DIR, PIE_CHUNK_NUM_PIC), 'Number of chunks required for successful matching')
        self.plot_bar(time_num, os.path.join(PIC_DIR, BAR_TIME_NUM_PIC), 'Duration required for successful matching')
        self.plot_pie(time_num, os.path.join(PIC_DIR, PIE_TIME_NUM_PIC), 'Duration required for successful matching')
        
        
    def get_key(self, k):
        match = re.match(r"(\d+)V(\d+)A", k)
        if match:
            x = int(match.group(1))
            y = int(match.group(2))
            return (x, y)
        return (0, 0)

    def plot_box(self, data, filename, title):
        """
        绘制箱线图
        :param data: 数据字典，键为类别，值为数据列表
        :param filename: 保存的文件名
        :param title: 图表标题
        """
        plt.figure(figsize=(12, 8))

        categories = list(data.keys())
        values = list(data.values())

        sns.boxplot(data=values, showfliers=False)

        plt.xticks(range(len(categories)), categories)
        plt.title(title)
        plt.ylabel('Values')

        plt.savefig(filename)
        print(f"Saved: {filename}")

    def plot_bar(self, counter, filename, title):
        """
        绘制条形图
        :param counter: 计数器字典，键为类别，值为计数
        :param filename: 保存的文件名
        :param title: 图表标题
        """
        combinations = list(counter.keys())
        counts = list(counter.values())

        plt.figure(figsize=(10, 6))
        plt.bar(combinations, counts, color='skyblue')

        plt.title(title)
        plt.xlabel('')
        plt.ylabel('Count')

        plt.xticks(rotation=45)
        plt.tight_layout()

        plt.savefig(filename)
        print(f"Saved: {filename}")

    def plot_pie(self, counter, filename, title):
        """
        绘制饼图
        :param counter: 计数器字典，键为类别，值为计数
        :param filename: 保存的文件名
        :param title: 图表标题
        """
        combinations = list(counter.keys())
        counts = list(counter.values())

        plt.figure(figsize=(8, 8))
        plt.pie(counts, labels=combinations, autopct='%1.1f%%', startangle=140, colors=plt.get_cmap('tab20').colors)

        plt.title(title)
        plt.savefig(filename)
        print(f"Saved: {filename}")
