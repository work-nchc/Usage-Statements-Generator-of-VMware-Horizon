from getpass import getpass
from _mssql import connect
from time import time
from io_log import *

def parser(data):
    return (
        data['Time'].isoformat(timespec='milliseconds')
        if 'Time' in data else '',
        data['UserSID'].lower()
        if 'UserSID' in data else '',
        data['DesktopId'].lower()
        if 'DesktopId' in data else '',
        data['UserDisplayName'].lower().split('\\')[-1]
        if 'UserDisplayName' in data else '',
        data['EntitlementSID'].lower()
        if 'EntitlementSID' in data else '',
        data['EntitlementDisplay'].lower().split('\\')[-1]
        if 'EntitlementDisplay' in data else '',
        data['MachineId'].lower()
        if 'MachineId' in data else '',
    )

# functions using side effects

def enable_pool(data):
    timestamp, sid_admin, pool = parser(data)[:3]
    name_admin = (
        data['ModuleAndEventText'].lower().split()[0].split('\\')[-1]
        if 'ModuleAndEventText' in data else '')

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
    name_admin = (
        data['ModuleAndEventText'].lower().split()[0].split('\\')[-1]
        if 'ModuleAndEventText' in data else '')

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
    if 'ModuleAndEventText' in data:
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
    name_vm = (
        data['ModuleAndEventText'].lower().split()[-1]
        if 'ModuleAndEventText' in data else '')
    
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
        .partition('machine ')[2].partition(' ')[0]
        if 'ModuleAndEventText' in data else '')

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
    name_vm = (
        data['ModuleAndEventText'].lower().split()[-1]
        if 'ModuleAndEventText' in data else '')
    
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
    name_admin = (
        data['ModuleAndEventText'].lower().split()[0].split('\\')[-1]
        if 'ModuleAndEventText' in data else '')
    name_vm = (
        data['ModuleAndEventText'].lower().split()[-1]
        if 'ModuleAndEventText' in data else '')
    username = (
        data['ModuleAndEventText'].lower().split()[4].split('\\')[-1]
        if 'ModuleAndEventText' in data else '')

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
    t = time()
    while True:
        
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
        time_end_all = update_log(qstr_event)['Time']
        update_log(qstr_user_events)
        update_log(qstr_config_changes)

        # Log Parsing
        {
            func_type[log_vdi[id_event]['EventType']](log_vdi[id_event])
            for id_event in sorted(log_vdi)
            if time_begin_all <= log_vdi[id_event]['Time'] < time_end_all
        }

        output_all(
            report,
            err,
            pools_enabled,
            pools_disabled,
            username_sid,
            user_pool,
            user_pool_deprived,
            vdi,
            time_end_all,
        )
        
        print('\r\t\t\t', round(time() - t, 3), end='     ')
