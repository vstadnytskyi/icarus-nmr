
##########################################################################################
### Logging section
##########################################################################################
    def SentEmail(self,event = b'test', category = b'user'):
        from pulse_generator_LL import pulse_generator
        from icarus_SL import icarus_sl
        import smtplib
        from time import strftime, localtime, time
        import platform
        snapshot = "\n \n -------  Variables Snapshot  ---------- \n \n"
        for record in vars(icarus_sl.inds).keys():
            snapshot += '%r = %r \r\n' %(record,vars(icarus_sl.inds)[record])
        for record in vars(icarus_sl.ctrls).keys():
            snapshot += '%r = %r \r\n' %(record,vars(icarus_sl.ctrls)[record])
        email_lst = []
        if category != 'None':
            for item in self.email_dic[category]:
                email_lst.append(item)
        print(email_lst)
        admin_email_lst = []
        for item in self.email_dic[b'administrator']:
            admin_email_lst.append(item )
        print(admin_email_lst)

        for email_item in email_lst:
            email = email_item[b'email']
            name = email_item[b'name']
            category = email_item[b'category']
            print(email,name,category)
            try:
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login("icarus.p.jump@gmail.com", "daedalus")
                if event == 'start':
                    msg = 'Subject: Test email.\n'
                    msg += "The code was started. at " +  strftime('%Y-%m-%d-%H-%M', localtime(time()))+'\n'
                    msg += snapshot

                elif event == 'subscription':
                    msg = 'Subject: icarus subscription\n'
                    msg += ("Dear %r, \n \n" % (name))
                    admins = ''
                    for item in admin_email_lst:
                        admins += item[b'email'] +' , '
                    msg += ("You have been subscribed to the high pressure apparatus %r as %r. Please contact your administrators (%r), if you have not authorized this subscription. \n \n" % (platform.node(),str(category),admins))
                    msg += ("Best Regards, \n Your Icarus")

                elif event == 'fault':
                    msg = 'Subject: Air Shutdown due to fault detected.\n'
                    msg += 'A Fault Detected at ' +  strftime('%Y-%m-%d-%H-%M', localtime(time())) +'\n'+ 'Fault = ' +str(self.fault)+'\n'
                    msg += 'The fault %r(%r) is detected. The warning counters are %r at index %r. The high pressure pump air flow was shut down' %(self.fault,
                                                                               self.fault_dic_description[self.fault],self.warn_counter,index)
                    msg += snapshot

                elif event == '':
                    msg = 'Subject: The experiment has started.\n'
                    msg += 'The logging has been initialize since the log bit was put low. The name of the log folder is' + '[name of the folder]' + '.\n '

                elif event == 'warning':
                    msg = 'Subject: Monitoring software is issued a warning.\n'
                    msg += 'Please consider servicing the experimental apparatus. Issued at ' +  strftime('%Y-%m-%d-%H-%M', localtime(time())) +'\n'+ 'Fault = ' +str(self.fault)+'\n'
                    msg += snapshot

                elif event == 'BufferOverflow':
                    msg = 'Buffer Overflow  at ' +  strftime('%Y-%m-%d-%H-%M', localtime(time()))+'\n'
                    msg += snapshot

                else:
                    msg = 'Subject: unknown reason to send email.\n'
                    msg += 'The server sent an email for unknown reason. \n'
                    msg += snapshot
                server.sendmail("icarus.p.jump@gmail.com", email, msg)
                server.quit()
            except:
                error(traceback.format_exc())

    def add_subscriber(self, name = {'category':'None', 'name': 'test user', 'email': 'v.stadnytskyi@gmail.com'}):
        try:
            self.email_dic[name[b'category']].append(name)
        except:
            error(traceback.format_exc())

    def delete_subscriber(self, name = {}):
        for cat_item in self.email_dic.keys():
            for item in cat_item:
                if item[b'email'] == name[b'email']:
                    self.email_dic[cat_item].pop(item)

    def pack_email_dic(self):
        import msgpack
        import msgpack_numpy as m
        self.email_dic_packed = msgpack.packb(self.email_dic, default=m.encode)


    def unpack_email_dic(self):
        import msgpack
        import msgpack_numpy as m
        return msgpack.unpackb(self.email_dic_packed , object_hook=m.decode)


    def logging_init(self):
        """
        initializes logging at the very beginning. Creates all necessary variables and objects.
        Has to be run once at the beginning of the server initialization
        """
        from os import makedirs, path
        from time import strftime, localtime, time
        from datetime import datetime
        from XLI.circular_buffer_LL import CBServer



        ##Email section
        self.email_lst = []
        self.email_lst.append('v.stadnytskyi@gmail.com')
        self.email_dic = {}
        self.email_dic[b'administrator'] = []
        self.email_dic[b'user'] = []
        self.email_dic[b'administrator'].append({b'name': 'Valentyn Stadnytskyi', b'email':'valentyn.stadnytskyi@nih.gov',b'category':'administrator',b'valid':None})
        self.email_dic[b'user'].append({b'name': 'Valentyn User', b'email':'v.stadnytskyi@gmail.com',b'category':'user',b'valid':None})

        self.pack_email_dic()


        self.logFolder =  ''
        self.logging_permanent_log_init()
        self.logging_permanent_log_append(message = 'new experiment started with log folder: %r' %(self.logFolder))


        if self.logging_state:
            self.logging_start()
            self.experiment_parameters_log()


        self.history_buffers_list = [b'pPre_0',
                                     b'pDepre_0',
                                     b'pPre_after_0',
                                     b'pDiff_0',
                                     b'tSwitchDepressure_0',
                                     b'tSwitchDepressureEst_0',
                                     b'tSwitchPressure_0',
                                     b'tSwitchPressureEst_0',
                                     b'gradientPressure_0',
                                     b'gradientDepressure_0',
                                     b'gradientPressureEst_0',
                                     b'gradientDepressureEst_0',
                                     b'riseTime_0',
                                     b'fallTime_0',
                                     b'pPre_1',
                                     b'pDepre_1',
                                     b'pPre_after_1',
                                     b'pDiff_1',
                                     b'tSwitchDepressure_1',
                                     b'tSwitchPressure_1',
                                     b'gradientPressure_1',
                                     b'gradientDepressure_1',
                                     b'fallTime_1',
                                     b'riseTime_1',
                                     b'period',
                                     b'delay',
                                     b'pressure_pulse_width',
                                     b'depressure_pulse_width',
                                     b'pump_stroke',
                                     b'depressure_valve_counter',
                                     b'pressure_valve_counter',
                                     b'leak_value',
                                     b'meanbit3'
                                     ]
        #history buffers order: arr[0,0] = period_idx, arr[1,0] = event_code, arr[2,0] = global_pointer, arr[3,0] = value
           ###dictionary with history circular buffer names
        self.history_buffers = {}
        for key in self.history_buffers_list:
            self.history_buffers[key] = CBServer(size = (4,self.history_buffer_size), var_type = 'float64')

    def logging_reset(self, pvname = '',value = '', char_val = ''):
        from os import makedirs, path
        from time import strftime, localtime, time
        from datetime import datetime
        from XLI.circular_buffer_LL import CBServer
        ###reset counters by grabbing local parameters from global
        self.counters_current = {b'pump':0,
            b'depressurize':0,
            b'pressurize':0,
            b'valve3':0,
            b'logging':0,
            b'D5':0,
            b'D6':0,
            b'period':0,
            b'delay':0,
            b'timeout':0,
            b'pump_stroke':0,
            b'periodic_update':0,
            b'periodic_update_cooling':0,
            b'emergency': 0} #emergency counter for leak detection
        #clear history buffers
        for key, values in self.history_buffers.items():
            self.history_buffers[key].clear()



    def experiment_parameters_log(self):
        """
        records all initial parameters of the experiment in the experiment_parameters.log file
        - DAQ frequency
        """
        from daq_LL import daq
        from pulse_generator_LL import pulse_generator
        f = open(self.logFolder + 'experiment_parameters' + '.log','w+')
        timeRecord = self.logtime

        f.write('####This experiment started at: %r \r\n'
                %(timeRecord))
        f.write('---Parameters for Event Detector LL--- \r\n')
        for record in vars(event_detector).keys():
            f.write('%r = %r \r\n' %(record,vars(event_detector)[record]))
        f.write('---Parameters for DAQ DL--- \r\n')
        for record in vars(daq).keys():
            f.write('%r = %r \r\n' %(record,vars(daq)[record]))
        f.write('---Parameters for Pulse Generator LL--- \r\n')
        for record in vars(pulse_generator).keys():
            f.write('%r = %r \r\n' %(record,vars(pulse_generator)[record]))

        f.close()

    def logging_start(self, dirname = ""):
        """
        this will create a new
        """
        from os import makedirs, path
        from time import strftime, localtime, time
        from datetime import datetime
        self.counters_current[b'period'] = 0
        self.logtime = time()
        if dirname == "":
            self.logFolder =  self.ppLogFolder + strftime('%Y-%m-%d-%H-%M-%S', localtime(time())) + '/'
        else:
            self.logFolder =  self.ppLogFolder + dirname +strftime('%Y-%m-%d-%H-%M-%S', localtime(time())) + '/'
        self.logging_permanent_log_append(message = 'new experiment started with log folder: %r' %(self.logFolder))
        self.logging_reset()
        if path.exists(path.dirname(self.logFolder)):
            pass
        else:
            makedirs(path.dirname(self.logFolder))
        timeRecord = self.logtime
        msg = '####This experiment started at: %r and other information %r \r\n' %(timeRecord,'and other information')
        open(self.logFolder + 'experiment.log','w').write(msg)
        msg = "b'time' , b'global_pointer', b'period_idx', b'event_code'"
        for key in self.history_buffers_list:
           msg += ' , ' + str(key)
        msg += '\r\n'
        open(self.logFolder + 'experiment.log','a').write(msg)



    def logging_event_append(self,dic = {},event_code = 0, global_pointer = 0, period_idx = 0):
        """
        - logs events into a file if self.logging_state == True
        - always appends current value to the logVariable_buffers[b'#key#'] where #key#
            can be found in self.logVariables dictionary
        """
        from os import makedirs, path
        from time import strftime, localtime, time
        from datetime import datetime
        from numpy import zeros
        from icarus_SL import icarus_SL
        arr = zeros((4,1))
        t = time()

        for key, value in dic.items():
            if key in self.history_buffers_list:
                arr[0,0] = period_idx
                arr[1,0] = event_code
                arr[2,0] = global_pointer
                arr[3,0] = value
                self.history_buffers[key].append(arr)
        icarus_SL.inds.history_buffers_value = None
        if self.logging_state:
            msg = self.logging_create_log_entry(dic = dic,event_code = event_code, global_pointer = global_pointer, period_idx = period_idx)
            msg += '\r\n'
            open(self.logFolder + 'experiment.log','a').write(msg)

    def logging_create_log_entry(self,dic = {},event_code = 0, global_pointer = 0, period_idx = 0, debug = False):
        from numpy import nan
        result = []
        result.append(time())
        result.append(global_pointer)
        result.append(period_idx)
        result.append(event_code)
        offset = len(result)
        for item in self.history_buffers_list:
            result.append(nan)
        for key, value in dic.items():
            idx = self.history_buffers_list.index(key)
            result[offset+idx] = value
        if debug:
            return result
        else:
            return str(result).replace('[','').replace(']','')



    def data_log_to_file(self,data,name = ''):
        from os import makedirs, path
        from time import strftime, localtime, time
        from datetime import datetime
        from numpy import savetxt, transpose
        sleep(0.1)
        #self.logFolder =  self.ppLogFolder + strftime('%Y-%m-%d-%H-%M', localtime(time())) + '/'
        if path.exists(path.dirname(self.logFolder)):
            pass
        else:
            makedirs(path.dirname(self.logFolder))
        #self.logFolder =  self.ppLogFolder + strftime('%Y-%m-%d-%H-%M', localtime(time())) + '/'
        if path.exists(path.dirname(self.logFolder + '/buffer_files/')):
            pass
        else:
            makedirs(path.dirname(self.logFolder + '/buffer_files/'))
        #data  = transpose(DAQ.RingBuffer.buffer[:,int(self.idx_event)-1000:int(self.idx_event)+1000])
        period_idx = self.counters_current[b'period']
        filename = str(time()) + '_'+ str(period_idx) + '_' + name + '.csv'
        dirname = '/buffer_files/'
        savetxt(self.logFolder +  dirname + filename, transpose(data), fmt='%.4e', delimiter=',', newline='\n', header='', footer='', comments='#Comments go here ')


    def logging_permanent_log_init(self):
        import platform
        from os import makedirs, path
        from time import strftime, localtime, time
        from datetime import datetime

        server_name = platform.node()
        if not path.isdir('log/'):
            makedirs('log/')
        self.perm_logfile_name = 'log/' + strftime('%Y-%m-', localtime(time())) + server_name +  '.log'
        self.perm_log_Folder =  self.ppLogFolder
        time_stamp = strftime('%Y-%m-%d-%H-%M-%S', localtime(time()))
        if not path.isfile(self.perm_logfile_name):
            txt = '%r: The permanent log file for the %r server of %r \r\n' %(time_stamp,server_name, strftime('%Y-%m', localtime(time())))
            open(self.perm_logfile_name,'w').write(txt)
            self.logging_permanent_log_append(message = 'log file created')
        else:
            self.logging_permanent_log_append(message = 'new succesful initialization of the permanent log file. File already exist')


    def logging_permanent_log_append(self, message):
        from time import strftime, localtime, time
        from datetime import datetime
        time_stamp = strftime('%Y-%m-%d-%H-%M', localtime(time()))
        if type(message) == str:
            txt = '%r : %r \n' %(time_stamp,message)
            open(self.perm_logfile_name,'a').write(txt)


##########################################################################################
###  History section and history buffers
##########################################################################################

    def history_append(self, lst = []):
        """
        appends values to circular buffers with keys according to the input dictionary(dic)
        """
        from numpy import zeros
        arr = zeros((4,1))
        t = time()
        for item in lst:
            for key, value in item.items():
                if key in self.history_buffers_list:
                    arr[0,0] = self.counters_current[b'period']
                    arr[1,0] = value[b'evt_code']
                    arr[2,0] = value[b'global_pointer']
                    arr[3,0] = value[b'value']
                    self.history_buffers[key].append(arr)
