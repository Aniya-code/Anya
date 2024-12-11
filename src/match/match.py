# matcher.py
import configparser

config = configparser.ConfigParser()
config.read('src/match/config.ini')
C = config.getint('DEFAULT', 'C')

class OnlineMatch:
    def __init__(self, tolerance, FP_LIST, MATCH_STATE) -> None:
        self.tolerance = tolerance # chunk-body的偏差上限
        self.FP_LIST = FP_LIST
        self.MATCH_STATE = MATCH_STATE
    

    def chunk_match(self, chunk_idx, chunk):
        for fp_idx, fp_obj in enumerate(self.FP_LIST):
            if not self.MATCH_STATE[fp_idx]:
                self.last_start_index = -1 
                self.last_end_index = -1 
            else:
                self.last_start_index = self.MATCH_STATE[fp_idx][-1]['start_index'] # 记录上一个找到的区间的开始索引
                self.last_end_index = self.MATCH_STATE[fp_idx][-1]['end_index']  # 记录上一个找到的区间的结束索引

            self.subarray_sum_with_tolerance(fp_idx, fp_obj, chunk_idx, chunk, tolerance = self.tolerance)

    def subarray_sum_with_tolerance(self, fp_idx, fp_obj, chunk_idx, target, tolerance = 2000):
        '''
        输入：一条指纹fp_obj；一个目标chunk
        输出：MATCH_STATE:{idx:, chunk:, start_idx:, end_idx:, subarray:, sum:, difference:,}
        '''
        sequence = fp_obj.sorted_fp
        format_list = fp_obj.format_fp
        prefix_sum_list, bin_prefix_sum_list = fp_obj.prefix_fp, fp_obj.prefix_fp_bin
        prefix_sum_dict, bin_prefix_sum_dict = fp_obj.prefix_dict, fp_obj.prefix_dict_bin

        n = len(sequence)
        # 遍历每个目标值
        bin_target = target // C
        tolerance = tolerance // C

        for i in range(n): #self.last_end_index+1, n): # O(n) ##
            bin_prefix_sum = bin_prefix_sum_list[i]

            for k in range(0, tolerance): 
                if bin_prefix_sum - bin_target + k in bin_prefix_sum_dict:
                    start_index = bin_prefix_sum_dict[bin_prefix_sum - bin_target + k]
                    
                    if i - start_index <= 8:
                        subarray = sequence[start_index:i] # 前闭后开
                        format_subarray = format_list[start_index:i]
                        audio_count = format_subarray.count('a')
                        video_count = format_subarray.count('v')
                        # if audio_count <= video_count: 
                        subarray_sum = prefix_sum_list[i] - prefix_sum_list[start_index] # O(1)
                        diff = target - subarray_sum
                        
                        # 更新MATCH_STATE
                        self.MATCH_STATE[fp_idx].append({
                            'idx' : chunk_idx,
                            'target': target,
                            'start_index': start_index,
                            'end_index': i-1,
                            'subarray': subarray,
                            'format_subarray': format_subarray,
                            'audio_count': audio_count,
                            'video_count': video_count,
                            'sum': subarray_sum,
                            'difference':  diff
                        })
                        break


    def result_parse(self):
        all_continuous_intervals = [None]*len(self.FP_LIST)
        for i in range(len(self.MATCH_STATE)):
            if not self.MATCH_STATE[i]:
                continue
            longest_interval = self.find_continuous_intervals(self.MATCH_STATE[i])
            all_continuous_intervals[i]=longest_interval
        return all_continuous_intervals
        
    
    def find_continuous_intervals(self, results):
        '''
        输入：从一条无序的results，[]
        输出：最长连续区间，[]
        '''
        results.sort(key=lambda x: (x['idx'], x['start_index']))

        all_intervals = []

        for result in results:
            placed = False
            for interval in all_intervals:
                if result['idx'] == interval[-1]['idx'] + 1 and result['start_index'] == interval[-1]['end_index'] + 1:
                    interval.append(result)
                    placed = True
                    # break

            if not placed:
                all_intervals.append([result])

        longest_interval = max(all_intervals, key=len)
        return longest_interval

    def find_longest_intervals(self, all_intervals):
        '''
        输入：匹配结果区间，[None, [], None,[]...]
        输出：最终结果区间，[（idx,[]）]
        '''
        
        # 获取最大长度
        max_length = max((len(interval) for interval in all_intervals if interval is not None), default=0)
        if max_length == 0:
            return []
        longest_intervals = []
        # 返回所有长度等于最大长度的子列表
        for index, intervals in enumerate(all_intervals):
            if not intervals :
                continue
            if len(intervals) == max_length:
                longest_intervals.append((index, intervals))
                
        return longest_intervals 
    
    