import os


class old_blocks:
    def __init__(self, block_type='milling', block=list()):
        self.block = block
        self.block_type = block_type


def get_number_after_letter(line, letter):
    value = letter
    allow_symbols = '0123456789.-'
    for symbol in line.partition(letter)[2]:
        if symbol in allow_symbols:
            value += symbol
        else:
            break
    return value


def get_number_parametr(line, letter):
    value = letter
    allow_symbols = '#0123456789'
    for symbol in line.partition(letter)[2]:
        if symbol in allow_symbols:
            value += symbol
        else:
            break
    return value


def add_to_error_log(exc, error):
    with open('error.log', 'a', encoding='UTF-8') as error_log:
        error_message = list()
        error_message.append('{mistake}, {comment}\n'.format(
            mistake=type(exc), comment=exc))
        error_message.append(error)
        error_message.append('\n')
        for mistakes in error_message:
            error_log.write(mistakes)


def load_config():
    current_path = os.path.join(os.path.abspath(''), 'data', 'config.txt')
    data = list()
    try:
        with open(current_path, 'r', encoding='UTF-8') as file:
            for line in file:
                if line.strip() != '':
                    data.append(line.partition('=')[2].strip())
        if not os.path.exists(data[0]):
            data[0] = os.path.join(os.path.abspath(''), 'CONVERT')
    except BaseException as exc:
        data[0] = os.path.join(os.path.abspath(''), 'CONVERT')
        error_message = f'Неверно сохранены данные внутри config.txt или файл отсутсвует.\n'
        add_to_error_log(exc, error_message)
    return data


def get_raw_macodell_blocks(path, file_name):
    all_frames = list()
    temp_buffer = list()
    write_head = True
    row_list = list()
    head_symbols = ('G5', 'M25', 'M0',
                    '(', '%', '<', '\n', ' ', 'O', 'GOTO', '#')
    try:
        with open(path, 'r', encoding='UTF-8') as file:
            for line in file:
                temp_buffer.append(line)
                if write_head and (not line.startswith(head_symbols)):
                    write_head = False
                    for element in temp_buffer:
                        if element.startswith('#'):
                            raise TypeError()
                    temp_line = temp_buffer.pop()
                    head_block = old_blocks('head', temp_buffer[:])
                    temp_buffer.clear()
                    temp_buffer.append(temp_line)
                    all_frames.append(head_block)
                elif not write_head and line.startswith('N'):
                    temp_line = temp_buffer.pop()
                    row_list.append(temp_buffer[:])
                    temp_buffer.clear()
                    temp_buffer.append(temp_line)
            row_list.append(temp_buffer[:])
            temp_buffer.clear()
            for element in row_list:
                found_G53 = False
                block_type = 'milling'
                for line in element:
                    if line.startswith('G53'):
                        found_G53 = True
                    elif line.startswith('IF[#1GT0]GOTO'):
                        block_type = 'old_milling'
                    elif line.startswith('G81'):
                        block_type = 'drilling'
                    elif line.startswith('G83'):
                        block_type = 'drilling'
                    elif line.startswith('G65P'):
                        block_type = 'subroutine'
                        if line.startswith('G65P200'):
                            found_G53 = True
                temp_buffer.extend(element)
                if found_G53:
                    head_block = old_blocks(block_type, temp_buffer[:])
                    all_frames.append(head_block)
                    temp_buffer.clear()
                    found_G53 = False
    except TypeError as exc:
        error_message = f'Слишком сложный файл для преобразования. Отклонено.\n'
        add_to_error_log(exc, error_message)
    except BaseException as exc:
        error_message = f'Не получилось преобразовать файл {file_name} отсутсвует.\n'
        add_to_error_log(exc, error_message)
    return all_frames


def convert_head_for_bumotec(block):
    new_head = list()
    for line in block:
        new_head.append(line)
        if line.startswith('O'):
            new_head.pop()
            if '(' in line:
                temp_line = ''.join(('<', line.partition('(')[0], '>\n'))
                new_head.append(temp_line)
                temp_line = ''.join(('(', line.partition('(')[2]))
                new_head.append(temp_line)
            else:
                temp_line = ''.join(('<', line.rstrip(), '>\n'))
                new_head.append(temp_line)
        elif line.startswith('G5'):
            new_head.pop()
        elif line.startswith('M25'):
            new_head.pop()
        elif line.startswith('M00'):
            new_head.pop()
        elif line.startswith('(I#701'):
            new_head.pop()
        elif line.startswith('GOTO'):
            new_head.pop()
    while True:
        if new_head[-1].startswith('\n') and len(new_head) > 0:
            new_head.pop()
        else:
            break
    new_head.append('\n')
    new_head.append('M148\n')
    new_head.append('M53\n')
    new_head.append('\n')
    new_head.append('GOTO10\n')
    new_head.append('\n')
    return new_head


def get_milling_block(block, number):
    new_block = list()
    end_of_frame = ['M9\n', 'G69\n', 'G49\n',
                    'M5\n', 'M53\n', 'M00\n', '\n', '\n']
    data = {'angle_c': '', 'angle_b': '', 'speed': 'S2000', 'tool_num': '',
            'feed': '', 'x_1': '', 'y_1': '', 'z_1': '', 'h_num': ''}
    begin_g806 = ('G806', 'G1001', 'G802')
    not_allowed_symbols = ('G54', 'G55', 'G56', 'G57', 'M03',
                           'G58', 'M3', 'G53', 'M0\n', 'M00\n', 'M9', 'S')
    find_s = ('(', '#', '\n', ' ')
    feeds = dict()
    for index, line in enumerate(block):
        new_block.append(line)
        if line.startswith(begin_g806):
            new_block.pop()
            data['angle_b'] = get_number_after_letter(line, 'B')
            data['angle_c'] = get_number_after_letter(line, 'C')
            if ('S') in line:
                data['speed'] = get_number_after_letter(line, 'S')
            data['feed'] = get_number_after_letter(line, 'F')
            data['x_1'] = get_number_after_letter(line, 'X')
            data['y_1'] = get_number_after_letter(line, 'Y')
            data['z_1'] = get_number_after_letter(line, 'Z')
            data['h_num'] = get_number_after_letter(line, 'H')
            data['h_num'] = ''.join(
                ('H', str(int(data['h_num'].strip().partition('H')[2]) - 11)))
            if not line.startswith('G802'):
                data['tool_num'] = get_number_after_letter(line, 'T')
            count = 1
            while count < 10:
                if block[index + count].startswith('S'):
                    data['speed'] = get_number_after_letter(
                        block[index + count], 'S')
                    break
                elif not block[index + count].startswith(find_s):
                    break
                count += 1
            if line.startswith('G802'):
                shrink_data = list()
                allow_shink = (' ', '\n', '(')
                while len(new_block) > 0:
                    if new_block[-1].startswith(allow_shink):
                        shrink_data.insert(0, new_block.pop())
                    elif new_block[-1].startswith('M12'):
                        new_block.pop()
                    else:
                        new_block.extend(end_of_frame[:])
                        number += 10
                        temp_mes = ''.join(('N', str(number), '\n'))
                        new_block.append(temp_mes)
                        for line_2 in shrink_data:
                            if not line_2.startswith('\n'):
                                new_block.append(line_2)
                        break
            temp_line = ''.join(
                ('M6', data['tool_num'], data['h_num'], data['angle_b'], '\n'))
            new_block.append(temp_line)
            temp_line = ''.join(
                ('M3', data['speed'], '\n'))
            new_block.append(temp_line)
            temp_line = ''.join(
                ('G0', data['angle_c'], '\n'))
            new_block.append(temp_line)
            if int(float(data['angle_b'].partition('B')[2])) != 0:
                new_block.append('G211\n')
                temp_line = ''.join(
                    ('G0X60Y0Z100', data['angle_b'], '\n'))
                new_block.append(temp_line)
                new_block.append('G49\n')
            temp_line = ''.join(
                ('G304X#510Y#511Z#512', data['angle_c'], '\n'))
            new_block.append(temp_line)
            temp_line = ''.join(
                ('G201X0Y0Z0', data['angle_b'], '\n'))
            new_block.append(temp_line)
            temp_line = ''.join(
                ('G1', data['x_1'], data['y_1'], data['z_1'], data['feed'], '\n'))
            new_block.append(temp_line)
        elif line.startswith(not_allowed_symbols):
            new_block.pop()
        elif line.startswith('M01'):
            new_block.pop()
            new_block.append('M12\n')
        elif line.startswith('#') and '=' in line:
            new_block.pop()
            new_feed = ''.join(('F', line.partition('=')[0]))
            if new_feed not in feeds:
                feeds[new_feed] = ''.join(
                    ('F', line.partition('=')[2].strip()))
        elif line.startswith('M1'):
            new_block.pop()
            new_block.append('M12\n')
        elif line.startswith('M8'):
            new_block.pop()
            new_block.append('M8M138\n')
        elif line.startswith('N'):
            new_block.pop()
            temp_mes = ''.join(('N', str(number), '\n'))
            new_block.append(temp_mes)
        if 'F#' in line:
            temp_feed = get_number_parametr(line, 'F')
            if temp_feed in feeds:
                temp_message = line.replace(temp_feed, feeds[temp_feed])
                new_block.pop()
                new_block.append(temp_message)
    while len(new_block) > 0:
        if new_block[-1].strip() == '':
            new_block.pop()
        else:
            break
    number += 10
    new_block.extend(end_of_frame)
    return new_block, number


def convert_into_bumotec(raw_blocks, path, old_file_name):
    bumotec_blocks = list()
    bumotec_blocks.extend(convert_head_for_bumotec(raw_blocks[0].block))
    new_file_name = ''.join(('bumotec_', old_file_name))
    current_path = os.path.join(path, new_file_name)
    try:
        number = 10
        for element in raw_blocks[1:]:
            if element.block_type == 'milling' or element.block_type == 'drilling':
                new_list, number = get_milling_block(element.block, number)
                bumotec_blocks.extend(new_list[:])
                new_list.clear()

        with open(current_path, 'w', encoding='UTF-8') as file:
            file.writelines(bumotec_blocks)
    except BaseException as exc:
        error_message = f'Возникла ошибка при конвертировании одного из кадров файла.\n'
        add_to_error_log(exc, error_message)


def save_config(last_path):
    current_path = os.path.join(os.path.abspath(''), 'data', 'config.txt')
    try:
        data = list()
        with open(current_path, 'r', encoding='UTF-8') as read_file:
            for line in read_file:
                data.append(line)
        with open(current_path, 'w', encoding='UTF-8') as write_file:
            new_path = ''.join(('current path=', last_path))
            write_file.writelines(new_path)
    except BaseException as exc:
        error_message = f'Ошибка при попытке сохранить новый путь в файл config.txt.\n'
        add_to_error_log(exc, error_message)
    return data


def main(current_path, data):
    # Clear an error.log file before run main script
    mistakes_path = os.path.join(os.path.abspath(''), 'error.log')
    if os.path.exists(mistakes_path):
        os.remove(mistakes_path)

    file_name = current_path.split('/')[-1]
    folder = '/'.join(current_path.split('/')[:-1])
    raw_blocks = get_raw_macodell_blocks(current_path, file_name)
    if not os.path.exists(os.path.join(os.path.abspath(''), 'error.log')):
        convert_into_bumotec(raw_blocks, folder, file_name)

    # Check if error.log exist in work folder
    without_mistakes = 0
    if os.path.exists(mistakes_path):
        without_mistakes = 1
    return without_mistakes
