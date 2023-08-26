import os


class old_blocks:
    def __init__(self, number='N10', block_type='milling', block=list()):
        self.number = number
        self.block = block
        self.block_type = block_type


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


def convert_into_bumotec(path, file_name):
    all_frames = list()
    temp_buffer = list()
    write_head = True
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
                            raise BaseException(
                                'Слишком сложный файл для преобразования. Отклонено.')
                    temp_line = temp_buffer.pop()
                    head_block = old_blocks('N0', 'head', temp_buffer[:])
                    temp_buffer.clear()
                    temp_buffer.append(temp_line)
                    all_frames.append(head_block)

    except BaseException as exc:
        error_message = f'Не получилось преобразовать файл {file_name} отсутсвует.\n'
        add_to_error_log(exc, error_message)
    return all_frames


def main():
    data = load_config()
    file_name = 'O1234.NC'
    current_path = os.path.join(data[0], file_name)
    new_bumotec_file = convert_into_bumotec(current_path, file_name)


main()
