from tkinter import messagebox
import json
import os

from files.config.parameters import cj_list, params
from files.config.CN_EN import eng_chn_li

eng_chn = params.eng_chn
person = params.person

def check_cj(person_data):
    got_new = False
    old_cj = person_data.get('cj_done', [])
    new_cj_list = old_cj.copy()
    total_add = 0
    new_names = []
    for cj in cj_list:
        if cj['name'] in old_cj:
            continue
        shuxing = cj['type']
        goal = cj['goal']
        a = False

        if shuxing == 'game_num':
            val = person_data.get('game_num', 0)
            if val >= goal: a = True
        elif shuxing == 'win_num':
            val = person_data.get('win_num', 0)
            if val >= goal: a = True
        elif shuxing == 'lose_num':
            val = person_data.get('lose_num', 0)
            if val >= goal: a = True
        elif shuxing == 'beat_hard':
            val = person_data.get('beat_hard', 0)
            if val >= goal: a = True
        elif shuxing == 'online_num':
            val = person_data.get('online_num', 0)
            if val >= goal: a = True
        elif shuxing == 'cj_win':
            val = person_data.get('cj_win', 0)
            if val >= goal: a = True
        elif shuxing == 'lian_win':
            val = person_data.get('lian_win_max', 0)
            if val >= goal: a = True
        elif shuxing == 'level10':
            val = person_data.get('level', 1)
            if val >= 10: a = True

        if a:
            new_cj_list.append(cj['name'])
            got_new = True
            new_names.append(cj['name'])
            qifen = int(cj['reward'].replace('云币+', ''))
            total_add += qifen

    if got_new:
        person_data['cj_done'] = new_cj_list
        person_data['YH_number'] = person_data.get('YH_number', 0) + total_add
        person_data['level'] = person_data['YH_number'] // 100 + 1
        msg = '恭喜达成成就：\n'
        for nm in new_names:
            for cj in cj_list:
                if cj['name'] == nm:
                    msg += f'{cj["name"]}  {cj["desc"]}  {cj["reward"]}\n'
        messagebox.showinfo(eng_chn_li[14][eng_chn], msg)
    return got_new

def apply_game_result(is_win, is_online=False, is_hard=False, is_cj=False):
    global person
    db_path = 'files\\YQ_DataBase.json'
    if not os.path.exists(db_path):
        db_path = 'files_old\\YQ_DataBase.json'
    f1 = open(db_path, 'r')
    rt = json.loads(f1.read())
    f1.close()
    if person.get('name') not in rt:
        rt[person['name']] = {}
    pdata = rt[person['name']]
    if 'game_num' not in pdata: pdata['game_num'] = 0
    if 'lose_num' not in pdata: pdata['lose_num'] = 0
    if 'beat_hard' not in pdata: pdata['beat_hard'] = 0
    if 'online_num' not in pdata: pdata['online_num'] = 0
    if 'cj_win' not in pdata: pdata['cj_win'] = 0
    if 'cj_done' not in pdata: pdata['cj_done'] = []
    if 'lian_win_max' not in pdata: pdata['lian_win_max'] = 0
    if 'lian_win_now' not in pdata: pdata['lian_win_now'] = 0

    if is_cj:
        pdata['cj_win'] = pdata.get('cj_win', 0) + 1
        pdata['win_num'] = pdata.get('win_num', 0) + 1
        pdata['lian_win_now'] = pdata.get('lian_win_now', 0) + 1
        if pdata['lian_win_now'] > pdata.get('lian_win_max', 0):
            pdata['lian_win_max'] = pdata['lian_win_now']
    else:
        pdata['game_num'] = pdata.get('game_num', 0) + 1
        if is_online:
            pdata['online_num'] = pdata.get('online_num', 0) + 1
        if is_win:
            pdata['win_num'] = pdata.get('win_num', 0) + 1
            pdata['lian_win_now'] = pdata.get('lian_win_now', 0) + 1
            if pdata['lian_win_now'] > pdata.get('lian_win_max', 0):
                pdata['lian_win_max'] = pdata['lian_win_now']
            if is_hard:
                pdata['beat_hard'] = pdata.get('beat_hard', 0) + 1
        else:
            pdata['lose_num'] = pdata.get('lose_num', 0) + 1
            pdata['lian_win_now'] = 0
    pdata['level'] = int(pdata.get('YH_number', 0)) // 100 + 1
    check_cj(pdata)
    with open('files\\YQ_DataBase.json', 'w') as f2:
        f2.writelines(json.dumps(rt))
    person.clear()
    params.person.clear()
    person.update(pdata)
    params.person.update(pdata)