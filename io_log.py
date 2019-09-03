from datetime import datetime
from os import mkdir, walk, replace
from shutil import copyfile

__all__ = (
    'time_begin_all',
    'ip',
    'filename_state',
    'qstr_event',
    'qstr_user_events',
    'qstr_config_changes',
    'output_all',
)

time_begin_all = datetime(2019, 4, 1)
ip = '172.16.1.15'
filename_state = '201903_filtered.sav'

qstr_event = (
    'SELECT '
        'EventID, '
        'EventType, '
        'Time, '
        'ModuleAndEventText, '
        'UserSID, '
        'DesktopId, '
        'MachineId '
    'FROM event WHERE EventType IN ('
        "'ADMIN_DESKTOP_ADDED', "
        "'ADMIN_REMOVE_DESKTOP_SUCCEEDED', "
        "'VLSI_DESKTOP_UPDATED', "
        "'ADMIN_ADD_DESKTOP_ENTITLEMENT', "
        "'ADMIN_REMOVE_DESKTOP_ENTITLEMENT', "
        "'AGENT_CONNECTED', "
        "'AGENT_ENDED', "
        "'ADMIN_DESKTOP_SESSION_LOGOFF', "
        "'AGENT_SHUTDOWN', "
        "'AGENT_STARTUP', "
        "'BROKER_MACHINE_OPERATION_DELETED')"
)
qstr_user_events = (
    'SELECT '
        'EventID, '
        'EventType, '
        'Time, '
        'ModuleAndEventText, '
        'UserDisplayName, '
        'UserSID, '
        'DesktopId, '
        'MachineId '
    'FROM user_events WHERE EventType IN ('
        "'AGENT_CONNECTED', "
        "'AGENT_ENDED')"
)
qstr_config_changes = (
    'SELECT '
        'EventID, '
        'EventType, '
        'Time, '
        'ModuleAndEventText, '
        'UserDisplayName, '
        'UserSID, '
        'DesktopId, '
        'EntitlementSID, '
        'EntitlementDisplay '
    'FROM config_changes WHERE EventType IN ('
        "'ADMIN_DESKTOP_ADDED', "
        "'ADMIN_REMOVE_DESKTOP_SUCCEEDED', "
        "'ADMIN_ADD_DESKTOP_ENTITLEMENT', "
        "'ADMIN_REMOVE_DESKTOP_ENTITLEMENT')"
)

def output_all(
    report,
    err,
    pools_enabled,
    pools_disabled,
    username_sid,
    user_pool,
    user_pool_deprived,
    vdi,
    time_end_all,
    ):
    pools_all = sorted(pools_enabled) + sorted(pools_disabled)
    suph_pool = {pool: 80.0 for pool in pools_all}
    with open('suph.csv') as input_suph:
        next(input_suph)
        for suph in input_suph:
            data = suph.replace(',', ' ').split()
            if 1 < len(data):
                suph_pool[data[0]] = float(data[1])
    
    report_users = {}
    
    for data in report:
        vm, name_vm, pool, sid, username, begin, end = data.strip().split('\t')
        if username not in report_users:
            report_users[username] = [
                ('begin\tend\tduration_hour\tpool\tSU_per_hour\tSU',)]
        time_begin = datetime.strptime(begin, '%Y-%m-%dT%H:%M:%S.%f')
        time_end = datetime.strptime(end, '%Y-%m-%dT%H:%M:%S.%f')
        if time_begin > time_end:
            time_end = time_begin
        dur = (time_end - time_begin).total_seconds() // 0.036 / 100000
        su = round(dur * suph_pool[pool], 8)
        report_users[username].append((
            begin, end, dur, pool, suph_pool[pool], su))

    for vm in sorted(vdi):
        name_vm, pool, sid, username, begin = vdi[vm]
        if username and username not in report_users:
            report_users[username] = [
                ('begin\tend\tduration_hour\tpool\tSU_per_hour\tSU',)]
        if username:
            time_begin = datetime.strptime(begin, '%Y-%m-%dT%H:%M:%S.%f')
            time_end = time_end_all
            if time_begin > time_end:
                time_end = time_begin
            dur = (time_end - time_begin).total_seconds() // 0.036 / 100000
            su = round(dur * suph_pool[pool], 8)
            report_users[username].append((
                begin, '', dur, pool, suph_pool[pool], su))
    
    for username in report_users:
        su_total = sum(data[-1] for data in report_users[username][1:])
        report_users[username].append(('SU_total', round(su_total, 8)))
    
    try:
        mkdir('temp')
        mkdir('users')
    except FileExistsError:
        pass
    
    for username in report_users:
        with open('temp/{}.csv'.format(username), 'w') as output_user:
            {output_user.write('\t'.join(map(str, data)) + '\n')
             for data in report_users[username]}

    with open('temp/report.log', 'w') as output_report:
        output_report.writelines(report)

    with open('temp/error.log', 'w') as output_err:
        output_err.writelines(err)

    with open('temp/state.sav', 'w') as output_state:
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

    entitle = {sid: [''] * len(pools_all) for sid in username_sid}

    for pool in pools_all:
        if pool in user_pool:
            for sid in user_pool[pool]:
                entitle[sid][pools_all.index(pool)] = pool
        if pool in user_pool_deprived:
            for sid in user_pool_deprived[pool]:
                entitle[sid][pools_all.index(pool)] = '#' + pool

    with open('temp/entitlement.log', 'w') as output_entitle:
        output_entitle.write('\t'.join(['sid', 'username'] + pools_all) + '\n')
        {output_entitle.write(
            '\t'.join([sid, username_sid[sid]] + entitle[sid]) + '\n')
         for sid in sorted(username_sid)}
    
    with open('temp/pool.log', 'w') as output_pool:
        output_pool.write('\n'.join(pools_all))
    
    temp = sorted(next(walk('temp'))[2])
    for filename in temp:
        if '.csv' == filename[-4:]:
            dst = 'users/' + filename
        else:
            dst = filename
        try:
            replace('temp/' + filename, dst)
        except OSError:
            pass
    copyfile('_vdi.dat', 'back.dat')
    try:
        replace('_vdi.dat', 'vdi.dat')
    except OSError:
        pass
    
    return None
