from getpass import getpass
from _mssql import connect
from datetime import datetime
from io_log import qstr_event, qstr_user_events, qstr_config_changes

ip = '172.16.1.15'

# functions using side effects

def enable_pool(data):
    time_event = data['Time']
    timestamp = time_event.isoformat(timespec='milliseconds')
    sid_admin = data['UserSID'].lower()
    pool = data['DesktopId'].lower()
    name_admin = data['ModuleAndEventText'].lower().split()[0].split('\\')[-1]

    if sid_admin and sid_admin not in username_sid:
        username_sid[sid_admin] = ''
    if sid_admin and name_admin:
        username_sid[sid_admin] = name_admin
    if pool and pool not in user_pool:
        user_pool[pool] = set()
    if pool and pool not in user_pool_deprived:
        user_pool_deprived[pool] = set()
    if pool and timestamp:
        pools_enabled.add(pool)
        pools_disabled.discard(pool)
        for vm in sorted(vdi):
            if vdi[vm][1] == pool and vdi[vm][2]:
                report.append('\t'.join([vm] + vdi[vm] + [timestamp]) + '\n')
            if vdi[vm][1] == pool:
                vdi[vm][2:] = '', '', ''
    else:
        err.append(str(data) + '\n')

    return None

def disable_pool(data):
    time_event = data['Time']
    timestamp = time_event.isoformat(timespec='milliseconds')
    sid_admin = data['UserSID'].lower()
    pool = data['DesktopId'].lower()
    name_admin = data['ModuleAndEventText'].lower().split()[0].split('\\')[-1]

    if sid_admin and sid_admin not in username_sid:
        username_sid[sid_admin] = ''
    if sid_admin and name_admin:
        username_sid[sid_admin] = name_admin
    if pool and pool not in user_pool:
        user_pool[pool] = set()
    if pool and pool not in user_pool_deprived:
        user_pool_deprived[pool] = set()
    if pool and timestamp:
        pools_disabled.add(pool)
        pools_enabled.discard(pool)
        for vm in sorted(vdi):
            if vdi[vm][1] == pool and vdi[vm][2]:
                report.append('\t'.join([vm] + vdi[vm] + [timestamp]) + '\n')
            if vdi[vm][1] == pool:
                vdi[vm][2:] = '', '', ''
    else:
        err.append(str(data) + '\n')

    return None

def update_pool(data):
    if ('(MODIFY: desktopSettings.enabled = true)'
        in data['ModuleAndEventText']):
        enable_pool(data)
    if ('(MODIFY: desktopSettings.enabled = false)'
        in data['ModuleAndEventText']):
        disable_pool(data)
    
    return None

def add_pool(data):
    time_event = data['Time']
    timestamp = time_event.isoformat(timespec='milliseconds')
    sid_admin = data['UserSID'].lower()
    name_admin = data['UserDisplayName'].lower().split('\\')[-1]
    pool = data['DesktopId'].lower()

    if sid_admin and sid_admin not in username_sid:
        username_sid[sid_admin] = ''
    if sid_admin and name_admin:
        username_sid[sid_admin] = name_admin
    if pool and pool not in user_pool:
        user_pool[pool] = set()
    if pool and pool not in user_pool_deprived:
        user_pool_deprived[pool] = set()
    if pool and timestamp:
        pools_enabled.add(pool)
        pools_disabled.discard(pool)
        for vm in sorted(vdi):
            if vdi[vm][1] == pool and vdi[vm][2]:
                report.append('\t'.join([vm] + vdi[vm] + [timestamp]) + '\n')
            if vdi[vm][1] == pool:
                vdi[vm][2:] = '', '', ''
    else:
        err.append(str(data) + '\n')

    if pool:
        user_pool_deprived[pool] |= user_pool[pool]
        user_pool[pool] = set()

    return None

def remove_pool(data):
    time_event = data['Time']
    timestamp = time_event.isoformat(timespec='milliseconds')
    sid_admin = data['UserSID'].lower()
    name_admin = data['UserDisplayName'].lower().split('\\')[-1]
    pool = data['DesktopId'].lower()

    if sid_admin and sid_admin not in username_sid:
        username_sid[sid_admin] = ''
    if sid_admin and name_admin:
        username_sid[sid_admin] = name_admin
    if pool and pool not in user_pool:
        user_pool[pool] = set()
    if pool and pool not in user_pool_deprived:
        user_pool_deprived[pool] = set()
    if pool and timestamp:
        pools_disabled.add(pool)
        pools_enabled.discard(pool)
        for vm in sorted(vdi):
            if vdi[vm][1] == pool and vdi[vm][2]:
                report.append('\t'.join([vm] + vdi[vm] + [timestamp]) + '\n')
            if vdi[vm][1] == pool:
                vdi[vm][2:] = '', '', ''
    else:
        err.append(str(data) + '\n')

    if pool:
        user_pool_deprived[pool] |= user_pool[pool]
        user_pool[pool] = set()

    return None

def entitle(data):
    time_event = data['Time']
    timestamp = time_event.isoformat(timespec='milliseconds')
    sid_admin = data['UserSID'].lower()
    name_admin = data['UserDisplayName'].lower().split('\\')[-1]
    pool = data['DesktopId'].lower()
    sid = data['EntitlementSID'].lower()
    username = data['EntitlementDisplay'].lower().split('\\')[-1]

    if sid_admin and sid_admin not in username_sid:
        username_sid[sid_admin] = ''
    if sid and sid not in username_sid:
        username_sid[sid] = ''
    if sid_admin and name_admin:
        username_sid[sid_admin] = name_admin
    if sid and username:
        username_sid[sid] = username
    if pool and pool not in user_pool:
        user_pool[pool] = set()
    if pool and pool not in user_pool_deprived:
        user_pool_deprived[pool] = set()
    if pool and sid:
        user_pool[pool].add(sid)
        user_pool_deprived[pool].discard(sid)
    if pool and sid and timestamp:
        for vm in sorted(vdi):
            if vdi[vm][1] == pool and vdi[vm][2] == sid:
                report.append('\t'.join([vm] + vdi[vm] + [timestamp]) + '\n')
                vdi[vm][2:] = '', '', ''
    else:
        err.append(str(data) + '\n')
    
    return None

def deprive(data):
    time_event = data['Time']
    timestamp = time_event.isoformat(timespec='milliseconds')
    sid_admin = data['UserSID'].lower()
    name_admin = data['UserDisplayName'].lower().split('\\')[-1]
    pool = data['DesktopId'].lower()
    sid = data['EntitlementSID'].lower()
    username = data['EntitlementDisplay'].lower().split('\\')[-1]
    
    if sid_admin and sid_admin not in username_sid:
        username_sid[sid_admin] = ''
    if sid and sid not in username_sid:
        username_sid[sid] = ''
    if sid_admin and name_admin:
        username_sid[sid_admin] = name_admin
    if sid and username:
        username_sid[sid] = username
    if pool and pool not in user_pool:
        user_pool[pool] = set()
    if pool and pool not in user_pool_deprived:
        user_pool_deprived[pool] = set()
    if pool and sid:
        user_pool_deprived[pool].add(sid)
        user_pool[pool].discard(sid)
    if pool and sid and timestamp:
        for vm in sorted(vdi):
            if vdi[vm][1] == pool and vdi[vm][2] == sid:
                report.append('\t'.join([vm] + vdi[vm] + [timestamp]) + '\n')
                vdi[vm][2:] = '', '', ''
    else:
        err.append(str(data) + '\n')
    
    return None

def log_in(data):
    time_event = data['Time']
    timestamp = time_event.isoformat(timespec='milliseconds')
    sid = data['UserSID'].lower()
    username = data['UserDisplayName'].lower().split('\\')[-1]
    pool = data['DesktopId'].lower()
    vm = data['MachineId'].lower()
    name_vm = data['ModuleAndEventText'].lower().split()[-1]
    
    if sid and sid not in username_sid:
        username_sid[sid] = ''
    if sid and username:
        username_sid[sid] = username
    if pool and pool not in user_pool:
        user_pool[pool] = set()
    if pool and pool not in user_pool_deprived:
        user_pool_deprived[pool] = set()
    if vm and vm not in vdi:
        vdi[vm] = ['', '', '', '', '']
    if vm and name_vm:
        vdi[vm][0] = name_vm
    if vm and pool:
        vdi[vm][1] = pool
    if vm and sid:
        vdi[vm][3] = username_sid[sid]
    if vm and sid and timestamp:
        if not vdi[vm][2]:
            vdi[vm][2] = sid
            vdi[vm][4] = timestamp
        elif vdi[vm][2] != sid:
            err.append(vdi[vm][2] + '\t' + str(data) + '\n')
            report.append('\t'.join([vm] + vdi[vm] + [timestamp]) + '\n')
            vdi[vm][2] = sid
            vdi[vm][4] = timestamp
    else:
        err.append(str(data) + '\n')
    
    return None

def log_off(data):
    time_event = data['Time']
    timestamp = time_event.isoformat(timespec='milliseconds')
    pool = data['DesktopId'].lower()
    vm = data['MachineId'].lower()
    name_vm = (
        data['ModuleAndEventText'].lower()
        .partition('machine ')[2].partition(' ')[0])

    if pool and pool not in user_pool:
        user_pool[pool] = set()
    if pool and pool not in user_pool_deprived:
        user_pool_deprived[pool] = set()
    if vm and vm not in vdi:
        vdi[vm] = ['', '', '', '', '']
    if vm and name_vm:
        vdi[vm][0] = name_vm
    if vm and pool:
        vdi[vm][1] = pool
    if vm and timestamp and vdi[vm][2]:
        report.append('\t'.join([vm] + vdi[vm] + [timestamp]) + '\n')
    if vm and timestamp:
        vdi[vm][2:] = '', '', ''
    else:
        err.append(str(data) + '\n')
    
    return None

def log_off_user(data):
    sid = data['UserSID'].lower()
    vm = data['MachineId'].lower()
    
    if sid and sid not in username_sid:
        username_sid[sid] = ''
    if vm and sid and vm in vdi and vdi[vm][2] and vdi[vm][2] != sid:
        err.append(vdi[vm][2] + '\t' + str(data) + '\n')
    
    time_event = data['Time']
    timestamp = time_event.isoformat(timespec='milliseconds')
    pool = data['DesktopId'].lower()
    name_vm = data['ModuleAndEventText'].lower().split()[-1]

    if pool and pool not in user_pool:
        user_pool[pool] = set()
    if pool and pool not in user_pool_deprived:
        user_pool_deprived[pool] = set()
    if vm and vm not in vdi:
        vdi[vm] = ['', '', '', '', '']
    if vm and name_vm:
        vdi[vm][0] = name_vm
    if vm and pool:
        vdi[vm][1] = pool
    if vm and timestamp and vdi[vm][2]:
        report.append('\t'.join([vm] + vdi[vm] + [timestamp]) + '\n')
    if vm and timestamp:
        vdi[vm][2:] = '', '', ''
    else:
        err.append(str(data) + '\n')
    
    return None

def admin_kick(data):
    time_event = data['Time']
    timestamp = time_event.isoformat(timespec='milliseconds')
    sid_admin = data['UserSID'].lower()
    name_admin = data['ModuleAndEventText'].lower().split()[0].split('\\')[-1]
    name_vm = data['ModuleAndEventText'].lower().split()[-1]
    username = data['ModuleAndEventText'].lower().split()[4].split('\\')[-1]

    if sid_admin and sid_admin not in username_sid:
        username_sid[sid_admin] = ''
    if sid_admin and name_admin:
        username_sid[sid_admin] = name_admin
    if name_vm and timestamp:
        for vm in sorted(vdi):
            if vdi[vm][0] == name_vm and vdi[vm][3]:
                if username and vdi[vm][3] != username:
                    err.append(vdi[vm][3] + '\t' + str(data) + '\n')
                report.append('\t'.join([vm] + vdi[vm] + [timestamp]) + '\n')
            if vdi[vm][0] == name_vm:
                vdi[vm][2:] = '', '', ''
    else:
        err.append(str(data) + '\n')
    
    return None

func_type = {
    'ADMIN_DESKTOP_ADDED': add_pool,
    'ADMIN_REMOVE_DESKTOP_SUCCEEDED': remove_pool,
    'VLSI_DESKTOP_UPDATED': update_pool,
    'ADMIN_ADD_DESKTOP_ENTITLEMENT': entitle,
    'ADMIN_REMOVE_DESKTOP_ENTITLEMENT': deprive,
    'AGENT_CONNECTED': log_in,
    'AGENT_ENDED': log_off_user,
    'ADMIN_DESKTOP_SESSION_LOGOFF': admin_kick,
    'AGENT_SHUTDOWN': log_off,
    'AGENT_STARTUP': log_off,
    'BROKER_MACHINE_OPERATION_DELETED': log_off,
}

with connect(ip, input(': '), getpass(''), database='Horizon_Event') as conn:
    time_begin_all = datetime.strptime(
        input('date begin YYYY-mm-dd (included): '), '%Y-%m-%d')
    time_end_all = datetime.strptime(
        input('date end YYYY-mm-dd (excluded): '), '%Y-%m-%d')
    filename_state = input('state file: ')
    filename = input('output base name: ')
    
    # Initialization
    pools_enabled = set()
    pools_disabled = set()
    username_sid = {}
    user_pool = {}
    user_pool_deprived = {}
    vdi = {}
    report = []
    err = []
    if filename_state:
        with open(filename_state) as input_state:
            for state in input_state:
                label, __, data = state.partition('\t')
                if data.strip():
                    if 'pools_enabled' == label:
                        pools_enabled = set(data.strip().split())
                    elif 'pools_disabled' == label:
                        pools_disabled = set(data.strip().split())
                    else:
                        key, __, value = data.partition('\t')
                        if 'username_sid' == label:
                            username_sid[key] = value.strip()
                        elif 'user_pool' == label:
                            user_pool[key] = set(value.split())
                        elif 'user_pool_deprived' == label:
                            user_pool_deprived[key] = set(value.split())
                        elif 'vdi' == label:
                            vdi[key] = value.split('\t')
                            vdi[key][-1] = vdi[key][-1].strip()
                        else:
                            err.append(state)

    # Log Filtering
    log_vdi = {}
    def update_log(qstr):
        conn.execute_query(qstr)
        for row in conn:
            for key in row:
                if None == row[key]:
                    row[key] = ''
            log_vdi[row['EventID']] = row
        return row
    update_log(qstr_event)
    update_log(qstr_user_events)
    update_log(qstr_config_changes)

    # Log Parsing
    {
        func_type[log_vdi[id_event]['EventType']](log_vdi[id_event])
        for id_event in sorted(log_vdi)
        if time_begin_all <= log_vdi[id_event]['Time'] < time_end_all
    }

    with open(filename + '.csv', 'w') as output_report:
        output_report.writelines(report)

    with open(filename + '.err', 'w') as output_err:
        output_err.writelines(err)

    with open(filename + '.sav', 'w') as output_state:
        output_state.write('pools_enabled\t{}\n'.format(
            '\t'.join(sorted(pools_enabled))))
        output_state.write('pools_disabled\t{}\n'.format(
            '\t'.join(sorted(pools_disabled))))
        {output_state.write('username_sid\t{}\t{}\n'.format(
            sid, username_sid[sid])) for sid in sorted(username_sid)}
        {output_state.write('user_pool\t{}\t{}\n'.format(
            pool, '\t'.join(sorted(user_pool[pool]))))
         for pool in sorted(user_pool)}
        {output_state.write('user_pool_deprived\t{}\t{}\n'.format(
            pool, '\t'.join(sorted(user_pool_deprived[pool]))))
         for pool in sorted(user_pool_deprived)}
        {output_state.write('vdi\t{}\t{}\n'.format(vm, '\t'.join(vdi[vm])))
         for vm in sorted(vdi)}
