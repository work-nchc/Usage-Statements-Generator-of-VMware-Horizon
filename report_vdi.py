from getpass import getpass
from pymssql import connect
from datetime import datetime
from shutil import copyfile
from io_log import ip, qstr_event, qstr_user_events, qstr_config_changes

def parser(data):
    return (
        data['Time'].isoformat(timespec='milliseconds'),
        data['UserSID'].lower(),
        data['DesktopId'].lower(),
        data['UserDisplayName'].lower().split('\\')[-1],
        data['EntitlementSID'].lower(),
        data['EntitlementDisplay'].lower().split('\\')[-1],
        data['MachineId'].lower(),
    )

# functions using side effects

def enable_pool(data):
    timestamp, sid_admin, pool = parser(data)[:3]
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
    timestamp, sid_admin, pool = parser(data)[:3]
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
    timestamp, sid_admin, pool, name_admin = parser(data)[:4]

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
    timestamp, sid_admin, pool, name_admin = parser(data)[:4]

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
    timestamp, sid_admin, pool, name_admin, sid, username = parser(data)[:6]

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
    timestamp, sid_admin, pool, name_admin, sid, username = parser(data)[:6]
    
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
    timestamp, sid, pool, username, *__, vm = parser(data)
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
    timestamp, __, pool, *__, vm = parser(data)
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
    timestamp, sid, pool, *__, vm = parser(data)
    name_vm = data['ModuleAndEventText'].lower().split()[-1]
    
    if sid and sid not in username_sid:
        username_sid[sid] = ''
    if vm and sid and vm in vdi and vdi[vm][2] and vdi[vm][2] != sid:
        err.append(vdi[vm][2] + '\t' + str(data) + '\n')
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
    timestamp, sid_admin = parser(data)[:2]
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
        input('beginning date YYYY-mm-dd (included): '), '%Y-%m-%d')
    time_end_all = datetime.strptime(
        input('ending date YYYY-mm-dd (excluded): '), '%Y-%m-%d')
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

    # Log Querying
    log_vdi = {}
    def update_log(qstr):
        cursor = conn.cursor(True)
        cursor.execute(qstr)
        for row in cursor:
            for key in row:
                if None == row[key]:
                    row[key] = ''
            log_vdi[row['EventID']] = row
        return row
    update_log(qstr_event)
    update_log(qstr_user_events)
    update_log(qstr_config_changes)
        
    with open('vdi.dat') as input_dat:
        for row in input_dat:
            if row.strip():
                id_event, *data = row.split('\t')
                id_event = int(id_event)
                if id_event not in log_vdi:
                    log_vdi[id_event] = {}
                log_vdi[id_event]['EventID'] = id_event
                if (data[0] or
                    'EventType' not in log_vdi[id_event]):
                    log_vdi[id_event]['EventType'] = data[0]
                log_vdi[id_event]['Time'] = datetime.strptime(
                    data[1], '%Y-%m-%dT%H:%M:%S.%f')
                if (data[2] or
                    'UserSID' not in log_vdi[id_event]):
                    log_vdi[id_event]['UserSID'] = data[2]
                if (data[3] or
                    'DesktopId' not in log_vdi[id_event]):
                    log_vdi[id_event]['DesktopId'] = data[3]
                if (data[4] or
                    'UserDisplayName' not in log_vdi[id_event]):
                    log_vdi[id_event]['UserDisplayName'] = data[4]
                if (data[5] or
                    'EntitlementSID' not in log_vdi[id_event]):
                    log_vdi[id_event]['EntitlementSID'] = data[5]
                if (data[6] or
                    'EntitlementDisplay' not in log_vdi[id_event]):
                    log_vdi[id_event]['EntitlementDisplay'] = data[6]
                if (data[7] or
                    'MachineId' not in log_vdi[id_event]):
                    log_vdi[id_event]['MachineId'] = data[7]
                data[-1] = data[-1].strip()
                if (data[-1] or
                    'ModuleAndEventText' not in log_vdi[id_event]):
                    log_vdi[id_event]['ModuleAndEventText'] = data[-1]
    
    with open('_vdi.dat', 'w') as output_dat:
        for id_event in sorted(log_vdi):
            output_dat.write(str(id_event) + '\t')
            output_dat.write(log_vdi[id_event].setdefault(
                'EventType', '') + '\t')
            output_dat.write(log_vdi[id_event].setdefault(
                'Time', datetime(1, 1, 1)
                ).isoformat(timespec='milliseconds') + '\t')
            output_dat.write(log_vdi[id_event].setdefault(
                'UserSID', '') + '\t')
            output_dat.write(log_vdi[id_event].setdefault(
                'DesktopId', '') + '\t')
            output_dat.write(log_vdi[id_event].setdefault(
                'UserDisplayName', '') + '\t')
            output_dat.write(log_vdi[id_event].setdefault(
                'EntitlementSID', '') + '\t')
            output_dat.write(log_vdi[id_event].setdefault(
                'EntitlementDisplay', '') + '\t')
            output_dat.write(log_vdi[id_event].setdefault(
                'MachineId', '') + '\t')
            output_dat.write(log_vdi[id_event].setdefault(
                'ModuleAndEventText', '') + '\n')
    
    copyfile('_vdi.dat', 'vdi.dat')
    
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
