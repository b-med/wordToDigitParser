#!/usr/bin/python


import sys
import pandas as pd
import numpy as np
import copy
import math

# Arguments :
input_file = sys.argv[1]


def sum_under_80(ns_list):
    n = 0
    for ns in ns_list :
        if ns in all_dic :
            n += all_dic[ns]
    return n



if __name__ == "__main__":

    input_array = np.array(pd.read_table(input_file, header=None))
    
    # Loading language files :
    upto100 = np.array(pd.read_table(
        'dic/chiffres.dic', delim_whitespace=True, header=None))
    k_and_higher = np.array(pd.read_table(
        'dic/milliers.dic',delim_whitespace=True,  header=None))
        # thousands, millions...
    ones = np.array(pd.read_table(
        'dic/un.dic', delim_whitespace=True, header=None))
    conjunctions = np.array(pd.read_table(
        'dic/liaisons.dic', header=None))


    all_array = np.concatenate((upto100[:,0], k_and_higher[:,0],
            conjunctions[:,0], ones[:,0]), axis=0).tolist()
    not_to_count = np.concatenate(
            (conjunctions[:,0], ones[:,0]), axis=0).tolist()


    # Conversion dictionary :
    all_to_dic = np.concatenate((upto100, k_and_higher, ones), axis=0).tolist()
    all_dic = {}
    for key_val in all_to_dic :
        all_dic[key_val[0]] = key_val[1]


    # Parse input file :
    for phrase in input_array :
        phrase = phrase[0] # one single phrase per line
        if '------' in phrase : # for display purpose
            print phrase
            continue

        ####################
        # Look for numbers :
        ####################

        number_list = [] # (in words)
        number = []
        for w_idx, w in enumerate(phrase.split()) :

            if w in all_array :
                # Avoid "les milliards" et "pour cent":
                if w in ['millions', 'milliards'] \
                        and phrase.split()[w_idx-1] not in all_array \
                        or w in ['cent', 'cents'] \
                        and phrase.split()[w_idx-1] in ['pour'] : 
                    continue
                number.append(w)

            # we have no more numbers (in words) ahead:
            if number and (w_idx == len(phrase.split())-1
                           or w not in all_array) :
                numb_to_count = copy.deepcopy(number)
                # remove uncountable words:
                for w_ntc in not_to_count :
                    while w_ntc in numb_to_count :
                        numb_to_count.remove(w_ntc)
                # if there are countable words:
                if len(numb_to_count) > 0 \
                        or ('un' in number and 'virgule' in number) :
                    number_list.append(number)
                number = []


        ####################
        # Convert phrase : 
        ####################

        # To convert bigger numbers first
        number_list.sort(lambda x,y: -cmp(len(x), len(y)))
        
        number_in_digits_list = [] # converted numbers
        for number in copy.deepcopy(number_list) :

            # remove the "et" conjunction :
            while "et" in number :
                number.remove("et")

            # Split to fractions, thousands, millions, billions... :
            prod_sum = [] # 12500.03 = 12*1000 + 500*1 + 3/100
            # numbers with fractional parts :
            if 'virgule' in number :
                virgule_index = number.index('virgule')
                prod_sum.append(
                        [number[virgule_index+1:], 'virgule'])
                number = number[0:virgule_index]

            for n_idx, n in enumerate(list(number)) :
                if n in k_and_higher :
                    if number[0:n_idx] :
                        prod_sum.append([number[0:n_idx], n])
                    else :
                        prod_sum.append([['un'], n])
                    number = number[n_idx+1:]

            # if it contains something between 0 and 999 :
            if number :
                prod_sum.append([number, 'un'])

            # Compute the numerical value of each of
            # fractions, thousands... (partial_prod_sum) :
            for idx_prod, prod in enumerate(prod_sum) :

                if prod[1] == 'virgule' :
                    # fractional part : remove the leading zeroes
                    zeros = 0
                    while 'ze1ro' in prod[0] :
                        prod[0].remove('ze1ro')
                        zeros += 1

                partial_prod_sum = 0
                # for the case of 100 :
                hundred = ''
                if  'cent' in prod[0] :
                    hundred = 'cent'
                elif 'cents' in  prod[0] :
                    hundred = 'cents'
                if hundred != '' :
                    idx_cent = prod[0].index(hundred)
                    # trim :
                    hundreds_tab = prod[0][0:idx_cent+1]
                    prod[0] = prod[0][idx_cent+1:]
                    # compute hundreds :
                    if len(hundreds_tab) == 1 :
                        n_tmp = 1
                    else :
                        # also for the case of "dix huit cent" for expl
                        n_tmp = sum_under_80(hundreds_tab[:-1])
                    partial_prod_sum += 100 * n_tmp
                # for the case of 80 :
                if "quatre vingt" in " ".join(prod[0]) :
                    partial_prod_sum += 80
                    # Trim :
                    prod[0] = prod[0][2:]
                partial_prod_sum += sum_under_80(prod[0])

                prod[0] = []
                if prod[1] == 'virgule' :
                    # fractional part : put back the leading zeroes
                    for i in range(zeros) :
                        prod[0].append('ze1ro')
                prod[0].append(partial_prod_sum)

            # Compute the sum of products :
            number_in_digits = 0
            for prod in prod_sum :
                if prod[1] == 'virgule' :
                    frac_part_len = 0
                    while 'ze1ro' in prod[0] :
                        frac_part_len += 1
                        prod[0] = prod[0][1:]
                    frac_part_len += len(str(prod[0][0]))
                    # 0.08 = 8/(10^2) :
                    number_in_digits += prod[0][0] / math.pow(10, frac_part_len)
                else :
                    if prod[1] in all_dic :
                        number_in_digits += prod[0][0] * all_dic[prod[1]]

            number_in_digits_list.append(number_in_digits)

        # Replace the numbers (in words) by
        # the computed numbers (in digits):
        conv_phrase = phrase
        for nb_idx, nb in enumerate(number_list) :
            conv_phrase = conv_phrase.replace(
                    " ".join(nb), str(number_in_digits_list[nb_idx]))

        print conv_phrase
