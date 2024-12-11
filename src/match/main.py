# main.py
import time
import csv
import os
from datetime import datetime
from collections import defaultdict
import configparser

from finger import FpPair, ChunkList
from log import log_match, log_error
from match import OnlineMatch
from plot import DataPlotter

config = configparser.ConfigParser()
config.read('src/match/config.ini')
TOLERANCE = config.getint('DEFAULT', 'TOLERANCE')
MIN_INPUT_IDX = config.getint('DEFAULT', 'MIN_INPUT_IDX')
MAX_INPUT_IDX = config.getint('DEFAULT', 'MAX_INPUT_IDX')
OFFLINE_FP_FILE = config.get('INPUT', 'OFFLINE_FP_FILE')
ONLINE_CHUNK_FILE = config.get('INPUT', 'ONLINE_CHUNK_FILE')


def main():
    correct = 0 # 匹配成功的指纹数
    num = 0 # 总指纹数
    
    # 用于画图分析：
    diff_distribution = defaultdict(list) # 记录v a 组合与body的差值分布
    xy_pair_count = defaultdict(int) # 记录v a 的个数组合数
    itag_pair_count = defaultdict(int) # 记录v a 的itag组合数
    chunk_num = defaultdict(int) # 记录匹配成功用的chunk数
    time_num = defaultdict(int) # 记录匹配成功用的时长

    start = time.time()
    
    with open(OFFLINE_FP_FILE, 'r', newline='') as file:
        reader = csv.DictReader(file)
        FP_LIST = [FpPair(row) for row in reader] 

    with open(ONLINE_CHUNK_FILE, 'r', newline='') as file:
        reader = csv.DictReader(file)
        for idx, row in enumerate(reader):
            num += 1
            MATCH_STATE = [[] for _ in range(len(FP_LIST))]
            chunk_list_obj = ChunkList(row)

            log_match('#'*10 + f"开始识别chunk序列 标答：{chunk_list_obj.url} {chunk_list_obj.quality}" + '#'*10)

            online_match = OnlineMatch(TOLERANCE, FP_LIST, MATCH_STATE)

            for chunk_idx, chunk in enumerate(chunk_list_obj.chunk_list):
                if chunk_idx == 0 or chunk_idx == 1:
                    continue
                
                if chunk_idx == MAX_INPUT_IDX:
                    log_match("=-=【匹配失败】=-=")
                    
                    log_error(chunk_list_obj.url)
                    break

                online_match.chunk_match(chunk_idx, chunk)
                if chunk_idx > MIN_INPUT_IDX:
                    all_continuous_intervals = online_match.result_parse()
                    longest_intervals = online_match.find_longest_intervals(all_continuous_intervals)
                    
                    # 判断：longest_intervals 代表唯一url
                    url_set = set()
                    for interval_tuple in longest_intervals:
                        fp_obj = FP_LIST[interval_tuple[0]]
                        url_set.add(fp_obj.url)
                
                    if len(url_set) == 1: # 有可能是唯一url,但多条指纹（v_itag+251或者v_itag+251-drc),有相同匹配长度,默认取后一个drc,取决于经验
                        tuple_ = longest_intervals[-1]
                        fp_obj = FP_LIST[tuple_[0]]
                        
                        log_match(f"【chunk_idx={chunk_idx} 匹配结果】：1个URL: Line{tuple_[0]}: {fp_obj.url}")

                        # 匹配成功
                        if fp_obj.url == chunk_list_obj.url:
                            # 模式一：匹配成功
                            correct += 1
                            time_key = 0
                            
                            for result in tuple_[1]:
                                idx = result['idx']
                                target = result['target']
                                start_index = result['start_index']
                                end_index = result['end_index']
                                subarray = result['subarray']
                                a_count = result['audio_count']
                                v_count = result['video_count']
                                sum_subarray = result['sum']
                                diff = result['difference']
                                
                                log_match(f"chunk_idx={idx}:{target} : 片段索引: {start_index}--{end_index},  子序列: {subarray} 格式：{v_count}V{a_count}A 差值: {diff}")


                                key = f"{v_count}V{a_count}A"
                                # 【1】记录diff
                                diff_distribution[key].append(diff)
                                # 【2】记录a v组合规则
                                xy_pair_count[key] += 1

                                time_key += a_count * 10
                            
                            log_match(f"=-=【匹配成功 {fp_obj.video_itag} {fp_obj.audio_itag}】=-=")
                            
                            # 【3】记录itag组合规则
                            itag_key = f"V:{fp_obj.video_itag}/A:{fp_obj.audio_itag}"
                            itag_pair_count[itag_key] += 1
                            
                            # 【4】记录匹配成功用的chunk数
                            num_key = len(tuple_[1])
                            chunk_num[num_key] += 1

                            # 【5】记录匹配成功用的时间（音频个数）
                            time_num[time_key] += 1 

                            break # 结束当前chunk序列
                        else:
                            # 模式二：碰撞
                            log_match(f"=-=【匹配碰撞 {fp_obj.video_itag} {fp_obj.audio_itag}】=-=")
                            
                            log_error(chunk_list_obj.url)
                            break
                    else:
                        log_match(f"【chunk_idx={chunk_idx} 临时结果】：{len(longest_intervals)}个url")
        # 统计结果
        correct = correct/num
        log_match(f"容忍度={TOLERANCE} 在线指纹数={num} 准确率={correct:.5f}")
        end = time.time()
        log_match(f"总耗时：{end-start:.5f} 平均耗时={(end-start)/num:.5f}\n")

        # 保存分析结果

        # 画图分析
        DataPlotter(diff_distribution, xy_pair_count, itag_pair_count, chunk_num, time_num)

if __name__ == '__main__':
    main()
