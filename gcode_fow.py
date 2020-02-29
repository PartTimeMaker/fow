import numpy
import re


def _get_first_rough_section(gcode_list, verbose=False):
    
    line_num = 0
    end_line_num = None
    z_position = None

    is_skirt_passed = False
    is_wall_outer_passed = False

    re_type = re.compile(r'^;TYPE:(?P<type>\S+)')
    re_z = re.compile(r'^G[01] .*Z(?P<z_position>\d+.?\d*)')
    for nnn in range(line_num, len(gcode_list)):
        this_line = gcode_list[nnn]

        #this_search = re.search(r'^;TYPE:(?P<type>\S+)', this_line)
        this_search = re_type.search(this_line)
        if this_search is not None:
            if this_search.group('type') == 'SKIRT':
                is_skirt_passed = True
                if verbose:
                    print(f'{line_num}: SKIRT \t-> {gcode_list[line_num]}')
            else:
                if is_skirt_passed == True:
                    if this_search.group('type') == 'WALL-OUTER':
                        is_wall_outer_passed = True
                        if verbose:
                            print(f'{line_num}: WALL-OUTER \t-> {gcode_list[line_num]}')
                        
        #this_search = re.search('^G[01] .*Z(?P<z_position>\d+.?\d*)', this_line)
        this_search = re_z.search(this_line)
        if this_search is not None:
            z_position = float(this_search.group('z_position'))
            if is_wall_outer_passed:
                end_line_num = line_num-1
                if verbose:
                    print(f'{end_line_num-1}: End+1 \t-> {gcode_list[end_line_num-1]}')
                    print(f'{end_line_num}: *End \t-> {gcode_list[end_line_num]}')
                    print(f'{end_line_num+1}: End+1 \t-> {gcode_list[end_line_num+1]}')
                break

        line_num = line_num + 1

    return 0, end_line_num, z_position
        


def _get_next_rough_section(gcode_list, start_line_num, layer_height_rough_list, prev_z_position, verbose=False):
    
    line_num = start_line_num
    end_line_num = None
    z_position = None

    is_include = False
    is_in_outer_wall = False

    re_type = re.compile(r'^;TYPE:(?P<type>\S+)')
    re_z = re.compile(r'^G[01] .*Z(?P<z_position>\d+.?\d*)')
    for nnn in range(line_num, len(gcode_list)):
        this_line = gcode_list[nnn]

        #this_search = re.search(r'^;TYPE:(?P<type>\S+)', this_line)
        this_search = re_type.search(this_line)
        if this_search is not None:
            if this_search.group('type') == 'WALL-OUTER':
                is_in_outer_wall = True
            else:
                if is_in_outer_wall == True:
                    is_in_outer_wall = False
                    is_include = True
                    start_line_num = line_num
                    if verbose:
                        print('-'*50)
                        print(f'{line_num-1}: Start-1 \t-> {gcode_list[line_num-1]}')
                        print(f'{line_num}: *Start \t-> {gcode_list[line_num]}')
                        print(f'{line_num+1}: Start+1 \t-> {gcode_list[line_num+1]}')

        #this_search = re.search('^G[01] .*Z(?P<z_position>\d+.?\d*)', this_line)
        this_search = re_z.search(this_line)
        if this_search is not None:
            if is_include:
                if float(this_search.group('z_position')) in layer_height_rough_list:
                    if prev_z_position < float(this_search.group('z_position')):
                        is_include = False
                        end_line_num = line_num - 1
                        z_position = float(this_search.group('z_position'))
                        if verbose:
                            print(f'{end_line_num-1}: End+1 \t-> {gcode_list[end_line_num-1]}')
                            print(f'{end_line_num}: *End \t-> {gcode_list[end_line_num]}')
                            print(f'{end_line_num+1}: End+1 \t-> {gcode_list[end_line_num+1]}')
                        break
    
        line_num = line_num + 1

    return start_line_num, end_line_num, z_position
        

def _get_next_fine_section(gcode_list, start_line_num, z_position_rough, layer_height_fine_list, verbose=False):

    line_num = start_line_num
    end_line_num = []
    z_position = 0
    start_line_num = []

    is_in_outer_wall = False
    prev_z_position = 0

    re_type = re.compile(r'^;TYPE:(?P<type>\S+)')
    re_z = re.compile(r'^G[01] .*Z(?P<z_position>\d+.?\d*)')
    for nnn in range(line_num, len(gcode_list)):
        this_line = gcode_list[nnn]

        #this_search = re.search(r'^;TYPE:(?P<type>\S+)', this_line)
        this_search = re_type.search(this_line)
        if this_search is not None:
            if this_search.group('type') == 'WALL-OUTER':
                is_in_outer_wall = True
            else:
                if is_in_outer_wall == True:
                    is_in_outer_wall = False
                    end_line_num.append(line_num - 1)
                    if verbose:
                        print(f'{line_num-2}: End-1 \t-> {gcode_list[line_num-2]}')
                        print(f'{line_num-1}: *End \t-> {gcode_list[line_num-1]}')
                        print(f'{line_num}: End+1 \t-> {gcode_list[line_num]}')
                    if z_position >= z_position_rough:
                        break

        #this_search = re.search('^G[01] .*Z(?P<z_position>\d+.?\d*)', this_line)
        this_search = re_z.search(this_line)
        if this_search is not None:
            if float(this_search.group('z_position')) in layer_height_fine_list:
                if prev_z_position < float(this_search.group('z_position')):
                    z_position = float(this_search.group('z_position'))
                    prev_z_position = z_position
                    if z_position <= z_position_rough:
                        start_line_num.append(line_num)
                        if verbose:
                            print('-'*50)
                            print(f'{line_num-1}: Start-1 \t-> {gcode_list[line_num-1]}')
                            print(f'{line_num}: *Start \t-> {gcode_list[line_num]}')
                            print(f'{line_num+1}: Start+1 \t-> {gcode_list[line_num+1]}')

        line_num = line_num + 1

    return start_line_num, end_line_num


def _get_diff_e_position(gcode_list, verbose=False):
    re_e_g1 = re.compile(r'(?P<prefix>^G[01] .*E)(?P<e_position>\d+.?\d*)')
    re_e_g92 = re.compile(r'(?P<prefix>^G92 .*E)(?P<e_position>\d+.?\d*)')

    this_e_position = 0
    this_diff_e_position = 0
    prev_e_position = 0

    e_position = []
    diff_e_position = []
    for nnn in range(len(gcode_list)):
        this_diff_e_position = 0
        
        this_search = re_e_g1.search(gcode_list[nnn])
        if this_search is not None:
            this_e_position = float(this_search.group('e_position'))
            this_diff_e_position = this_e_position - prev_e_position
            
        this_search = re_e_g92.search(gcode_list[nnn])
        if this_search is not None:
            this_e_position = float(this_search.group('e_position'))
            
        e_position.append(this_e_position)
        diff_e_position.append(this_diff_e_position)
        prev_e_position = this_e_position

    if verbose:
        print(f'nnn:     \te_position:     \tdiff_e_position    \tgcode')
        for nnn in range(len(e_position)):
            print(f'{nnn}\t\t{e_position[nnn]}\t\t{diff_e_position[nnn]:.5f}\t\t{gcode_list[nnn]}')
    
    return e_position, diff_e_position
            
def make_fow_gcode(gcode_file_rough, gcode_file_fine, gcode_file_new, layer_height_init, layer_height_rough, layer_height_fine):

    #### read input gcode files
    with open(gcode_file_rough, 'r') as fid:
        gcode_rough = fid.readlines()
    print(f'File name(rough): {gcode_file_rough}\t ({len(gcode_rough)} lines)')

    with open(gcode_file_fine, 'r') as fid:
        gcode_fine = fid.readlines()
    print(f'File name(fine): {gcode_file_fine}\t ({len(gcode_fine)} lines)')

    ####
    layer_height_rough_list = [round(layer_height_init + nnn*layer_height_rough,3) for nnn in range(round(500/layer_height_rough))]
    layer_height_fine_list = [round(layer_height_init + nnn*layer_height_fine,3) for nnn in range(round(500/layer_height_fine))]
    

    #### get sections from rough and fine gcode files
    from_line_num = []
    to_line_num = []
    line_src = []

    s_rough, e_rough, z_rough = _get_first_rough_section(gcode_rough)
    print(f'[R] {s_rough} ~ {e_rough} (z: {z_rough})')
    from_line_num.append(s_rough)
    to_line_num.append(e_rough)
    line_src.append('R')

    s_fine, e_fine = _get_next_fine_section(gcode_fine, e_rough, z_rough, layer_height_fine_list)
    print(f'[F] {s_fine} ~ {e_fine}')
    for nnn in range(len(s_fine)):
        from_line_num.append(s_fine[nnn])
        to_line_num.append(e_fine[nnn])
        line_src.append('F')

    while True:
        
        s_rough, e_rough, z_rough = _get_next_rough_section(gcode_rough, e_rough+1, layer_height_rough_list, z_rough)
        print(f'[R] {s_rough} ~ {e_rough} (z: {z_rough})')
        from_line_num.append(s_rough)
        to_line_num.append(e_rough)
        line_src.append('R')
        if e_rough is None: 
            break
            
        s_fine, e_fine = _get_next_fine_section(gcode_fine, e_fine[-1]+1, z_rough, layer_height_fine_list)
        print(f'[F] {s_fine} ~ {e_fine}')
        for nnn in range(len(s_fine)):
            from_line_num.append(s_fine[nnn])
            to_line_num.append(e_fine[nnn])
            line_src.append('F')


    #### inspect section start and end lines 
    
    # for nnn in range(0,len(from_line_num)):
    #     if line_src[nnn] == 'F':
    #         print(f'[{line_src[nnn]}]\t{from_line_num[nnn]}\t{to_line_num[nnn]}\n\t{gcode_fine[from_line_num[nnn]]}\t{gcode_fine[to_line_num[nnn]]}')
    #     elif line_src[nnn] == 'R':
    #         if to_line_num[nnn] == None:
    #             print(f'[{line_src[nnn]}]\t{from_line_num[nnn]}\t{to_line_num[nnn]}\n\t{gcode_rough[from_line_num[nnn]]}\t{gcode_rough[-1]}')
    #         else:
    #             print(f'[{line_src[nnn]}]\t{from_line_num[nnn]}\t{to_line_num[nnn]}\n\t{gcode_rough[from_line_num[nnn]]}\t{gcode_rough[to_line_num[nnn]]}')
        
    #### calculate delta e_position
    e_position_rough, diff_e_position_rough = _get_diff_e_position(gcode_rough)
    e_position_fine, diff_e_position_fine = _get_diff_e_position(gcode_fine)
        
    #### write to new file
    
    re_e_g1 = re.compile(r'(?P<prefix>^G[01] .*E)(?P<e_position>\d+.?\d*)')    
    gcode_new = []
    this_e_position = 0
    for nnn in range(0,len(line_src)):
        if line_src[nnn] == 'F':
            for mmm in range(from_line_num[nnn], to_line_num[nnn]+1):
                this_e_position = this_e_position+diff_e_position_fine[mmm]
                this_gcode_line = re_e_g1.sub(r'\g<prefix>'+f'{this_e_position:.5f}', gcode_fine[mmm])
                gcode_new.append(this_gcode_line)
        elif line_src[nnn] == 'R':
            if to_line_num[nnn] is None:
                for mmm in range(from_line_num[nnn], len(gcode_rough)):
                    this_e_position = this_e_position+diff_e_position_rough[mmm]
                    this_gcode_line = re_e_g1.sub(r'\g<prefix>'+f'{this_e_position:.5f}', gcode_rough[mmm])
                    gcode_new.append(this_gcode_line)
            else:
                for mmm in range(from_line_num[nnn], to_line_num[nnn]+1):
                    this_e_position = this_e_position+diff_e_position_rough[mmm]
                    this_gcode_line = re_e_g1.sub(r'\g<prefix>'+f'{this_e_position:.5f}', gcode_rough[mmm])
                    gcode_new.append(this_gcode_line)

    with open(gcode_file_new, 'w') as fid:
        fid.writelines(gcode_new)



if __name__ == '__main__':
    


    make_fow_gcode(r'F:\round_cylinder_test_0_3.gcode',
        r'F:\round_cylinder_test_0_1.gcode',
        r'F:\round_cylinder_test_new.gcode',
        0.2, 0.3, 0.1)

    