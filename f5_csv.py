
# coding:utf-8


import csv
from optparse import OptionParser
from f5.bigip import ManagementRoot
import os
import platform

parser = OptionParser()
parser.add_option("-a", "--address", dest="address", help=" IP address of F5 bigip")
parser.add_option("-u", "--username", dest="username", help="admin user name")
parser.add_option("-p", "--password", dest="password", help="admin password")
options, args = parser.parse_args()

ip = options.address
username = options.username
password = options.password

try:
    if not ip:
        print('ip地址未输入,请按照如下的格式输入')
        raise Exception
    if not username:
        print('username用户名未输入,请按照如下的格式输入')
        raise Exception

    if not password:
        print('password用户密码未输入,请按照如下的格式输入')
        raise Exception


except Exception as e:
    print("请再次输入正确命令: python 文件名 -a ip地址 -u 用户名 -p 密码")
    exit()
try:
    mgmt_root = ManagementRoot(ip, username, password)
    # print(" ip + username + pwd ---> ok!")
    vs_list = mgmt_root.tm.ltm.virtuals.get_collection()


except Exception as e:
    print('输入错误,请按照以下格式,正确输入')
    print("请再次输入正确命令: python 文件名 -a ip地址 -u 用户名 -p 密码")
    exit()


def writecsv3(csvfilepath):
    # print("writecsv3 come!!")
    headers = ['分区名称', 'vs系统名称', 'vs对外服务地址与端口', 'pool名称', '服务器实际地址与端口']
    # headers = []
    # for i in headers_1:
    #     headers.append(i.decode("utf-8").encode("gbk"))
    rows = []
    dic_list = []

    for vs in vs_list:
        dic = {}
        if vs.partition == 'Common':
            # print(" Common partition")

            # print("  vs.partition--->", vs.partition)
            partition_name = vs.partition

            vs_name = vs.name
            # print("  vs_name--->", vs_name)

            dic['分区名称'] = partition_name  # 1. 分区名称

            dic['vs系统名称'] = vs_name  # 2. vs名称

            destination = vs.destination
            ip_port = destination.split('/')[-1]  # 3. vs对外服务地址与端口  192.168.200.111:111
            # print("  ip_port--->", ip_port)

            dic['vs对外服务地址与端口'] = ip_port

            pool = getattr(vs, 'pool', None)
            # print("  pool--->", pool)

            if pool is None:
                dic['pool名称'] = ''
                dic['服务器实际地址与端口'] = ''

            else:
                try:
                    pool_name = pool.split('/')[-1]  # 4. pool_name √
                    # print("  pool_name--->", pool_name)

                    dic['pool名称'] = pool_name
                    pool_ = mgmt_root.tm.ltm.pools.pool.load(name=pool_name)
                    member_address_list = []
                    for mem in pool_.members_s.get_collection():
                        if mem:
                            member_address = mem.address
                            member_all_name = mem.name

                            member_port = member_all_name.rsplit(':')[-1]
                            member_address_port = member_address + ":" + str(member_port)  # 5. '服务器实际地址与端口'
                            # print("  member_address_port--->", member_address_port)

                            member_address_list.append(member_address_port)

                    dic['服务器实际地址与端口'] = member_address_list

                except Exception as error:
                    print(partition_name + '出现问题' + ':' + str(error))
            # print("dic---->",dic)
        else:
            # print(" other partition")
            partition_name = vs.partition
            # print("partition_name=====>",partition_name)
            vs_name = vs.name
            dic['分区名称'] = partition_name  # 1. 分区名称
            dic['vs系统名称'] = vs_name  # 2. vs名称

            destination = vs.destination
            ip_port = destination.split('/')[-1]  # 3. vs对外服务地址与端口  192.168.200.111:111
            dic['vs对外服务地址与端口'] = ip_port

            pool = getattr(vs, 'pool', None)

            if pool is None:
                dic['pool名称'] = ''
                dic['服务器实际地址与端口'] = ''

            else:
                try:
                    pool_name = pool.split('/')[-1]  # 4. pool_name √
                    # print("pool_name",pool_name)
                    dic['pool名称'] = pool_name
                    subpath = getattr(vs, 'subPath', '')
                    member_address_list1 = []
                    if subpath:
                        pool_ = mgmt_root.tm.ltm.pools.pool.load(name=pool_name, partition=partition_name,
                                                                 subPath=subpath)
                        for mem in pool_.members_s.get_collection():
                            if mem:
                                member_address = mem.address
                                member_all_name = mem.name

                                member_port = member_all_name.rsplit(':')[-1]
                                member_address_port = member_address + ":" + str(member_port)  # 5. '服务器实际地址与端口'
                                member_address_list1.append(member_address_port)
                    else:
                        pool_ = mgmt_root.tm.ltm.pools.pool.load(name=pool_name, partition=partition_name)
                        for mem in pool_.members_s.get_collection():
                            if mem:
                                member_address = mem.address
                                member_all_name = mem.name

                                member_name = member_all_name.rsplit(':')[0]
                                member_port = member_all_name.rsplit(':')[-1]
                                member_address_port = member_address + ":" + str(member_port)  # 5. '服务器实际地址与端口'
                                member_address_list1.append(member_address_port)

                    dic['服务器实际地址与端口'] = member_address_list1
                except Exception as error:
                    print(partition_name + '出现问题' + ':' + str(error))

        if dic:
            dic_list.append(dic)  # dic_list 此dict_list见下方

    for dic in dic_list:

        server_ip = dic.get('服务器实际地址与端口')
        if server_ip:
            count = len(server_ip)
            for i in range(count):
                space_dic = {'分区名称': '', 'vs系统名称': '', 'vs对外服务地址与端口': '', 'pool名称': '', '服务器实际地址与端口': ''}

                if i == 0:
                    dic['服务器实际地址与端口'] = server_ip[i]  # 80
                    rows.append(dic)

                else:
                    space_dic['服务器实际地址与端口'] = server_ip[i]
                    rows.append(space_dic)

        else:
            dic['服务器实际地址与端口'] = ''
            rows.append(dic)
        # print(rows)
    # print("rows======>", rows)

    with open(csvfilepath, 'w+') as f:
        f_csv = csv.DictWriter(f, fieldnames=headers)
        f_csv.writeheader()
        f_csv1 = csv.DictWriter(f, headers)
        f_csv1.writerows(rows)

    # 在linux下,再运行这条指令,因为linux默认zh_CN.utf-8编码,而windows是gbk编码,所以传输之后会乱码

    sys_new = platform.system()
    if sys_new == "Linux":
        os.system('iconv -f UTF-8 -t GBK f5_write.csv -o f5_csv.csv')
        os.remove('f5_write.csv')


if __name__ == '__main__':

    try:
        import platform

        sys = platform.system()
        if sys == "Windows":
            file_name = r'f5_csv.csv'
        elif sys == "Linux":
            file_name = r'f5_write.csv'
        else:
            file_name = r'f5_write.csv'

        writecsv3(file_name)

    except Exception as e:
        print(e)
