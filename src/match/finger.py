# finger.py
import configparser

config = configparser.ConfigParser()
config.read('src/match/config.ini')
C = config.getint('DEFAULT', 'C')

class FpPair:
    def __init__(self, row) -> None:
        self.ID = row['ID']
        self.url = row['url']
        self.video_itag = row['video_itag']
        self.video_quality = row['video_quality']
        self.video_format = row['video_format']
        self.audio_itag = row['audio_itag']
        self.audio_quality = row['audio_quality']
        self.audio_format = row['audio_format']
        self.video_fp = list(map(int, row['video_fp'].split('/')))
        self.video_timeline = list(map(int, row['video_timeline'].split('/')))
        self.audio_fp = list(map(int, row['audio_fp'].split('/')))
        self.audio_timeline = list(map(int, row['audio_timeline'].split('/')))
        self.sorted_fp, self.format_fp = self.get_sorted_fp()
        self.prefix_fp, self.prefix_fp_bin = self.get_prefix_fp()
        self.prefix_dict, self.prefix_dict_bin = self.get_prefix_dict()

    def get_sorted_fp(self): 
        i, j = 0, 0
        sorted_fp, format_fp = [], []
        while i < len(self.video_fp)-1 and j < len(self.audio_fp):
            while i < len(self.video_fp)-1  and self.video_timeline[i+1] < self.audio_timeline[j]: # 每个视频段结束时间，要早于下一音频段开始时间
                sorted_fp.append(self.video_fp[i])
                format_fp.append('v')
                i +=1
            sorted_fp.append(self.audio_fp[j])
            format_fp.append('a')
            j += 1
        return sorted_fp[:100], format_fp[:100]
    
    def get_prefix_fp(self):
        prefix_list = [0] * (len(self.sorted_fp) + 1)
        for i in range(0, len(self.sorted_fp)):
            prefix_list[i+1] = prefix_list[i] + self.sorted_fp[i]
        prefix_list_bin = [item//C for item in prefix_list]
        return prefix_list, prefix_list_bin
    
    def get_prefix_dict(self):
        prefix_dict, prefix_dict_bin = {},{}
        for idx, value in enumerate(self.prefix_fp):
            prefix_dict[value] = idx
            prefix_dict_bin[value//C] = idx
        return prefix_dict, prefix_dict_bin
    

        

class ChunkList:
    def __init__(self, row) -> None:
        self.url = row['url']
        self.quality = row['quality']
        self.chunk_list = list(map(int, row['chunk_list'].split('/')))
