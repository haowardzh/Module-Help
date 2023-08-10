'''
------------------------------------------------------------------
      _eem.py -- Python Package for EEM Actions / CLI extensions

      December 2016, Anbalagan V

      Copyright (c) 2016-2020 by Cisco Systems, Inc.
      All rights reserved.
------------------------------------------------------------------
'''

import base64
import time
import abc
import xml.etree.ElementTree as ElementTree
import os, subprocess

RES_SUCCESS = 0
RES_DATA = 2
RES_ERR_SEVERITY = 3
RES_ERR_CODE  = 4
RES_ERR_MSG = 5

EEM_DATA_FORMAT = 1
EEM_USER_VARIABLES = None
EEM_BUILTIN = None
EEM_BUILTIN_MULTI = None


def _eem_encode_base64(message):

    return(base64.b64encode(str(message).encode()).decode())

def _eem_decode_base64(message):

    if _eem_decode_base64 is not None:
       return(base64.b64decode(message))
    else:
       return None


def get_vty_number( message ) :

    decoded_output = _eem_decode_base64(message)

    root = ElementTree.fromstring(decoded_output)
    for item in root.iter('output') :
        return item.text



def get_command_response(input_message , type =  1) :

    command_status = []
    command_output = []

    decoded_output = _eem_decode_base64(input_message)

    root = ElementTree.fromstring(decoded_output)

    for item in root.iter('mlang-response') :
        for c in item.getchildren() :
            if c is not None:
               command_status.append(c.text)

    ''' The type 1 indicates the status output '''
    if type == 1 :
            return command_status

    for item in root.iter('output') :
        for c in item.getchildren() :
           command_output.append(c.text)

    return  command_status, command_output


def get_env_response(input_message , type = 1) :

    command_status = {} 
    flag = 0 
    iter = 0
    tmp_d = {}
    key = ""
    value = ""
    item = {}
    final_d = {}

    decoded_output = _eem_decode_base64(input_message) 
    root = ElementTree.fromstring(decoded_output)

    for i in root.iter('env_vars') :
        for c in i.getchildren() :
           if c is not None:
             for d in c.getchildren() :
               if iter == 0 :
                   event_is = _eem_decode_base64(d.text)
                   iter = 1
               else:
                if d is not None:
                  if d.text is not None:
                    if flag == 0:
                       key = _eem_decode_base64(d.text)
                       flag = 1
                    else :
                       value =  _eem_decode_base64(d.text) 
                       item[key] = value
                       flag = 0
                  else :
                   value = str('-')
                   flag = 0
             if type == 1 :
                   tmp_d = item 
             else:
                   tmp_d[event_is] = item 
                   item = {} 
                   iter = 0
           final_d = tmp_d
    
    return final_d



def get_user_response(input_message , type =  1) :

    command_status = {}
    flag = 0
    tmp_d = {}
    key = ""
    value = ""
    item = {}
    final_d = {}

    decoded_output = _eem_decode_base64(input_message)

    root = ElementTree.fromstring(decoded_output)

    for i in root.iter('env_vars') :
             for d in i.getchildren() :
                if d is not None:
                  if d.text is not None:
                    if flag == 0:
                       key = _eem_decode_base64(d.text)
                       flag = 1
                    else :
                       value =  _eem_decode_base64(d.text)
                       item[key] = value
                       flag = 0
                  else :
                   value = str('-')
                   flag = 0
    final_d = item

    return final_d



def get_response(input_message) :

    output_list = []
    decoded_output = _eem_decode_base64(input_message)
    
    root = ElementTree.fromstring(decoded_output)

    for item in root.iter('output') :
        for c in item.getchildren() :
            output_list.append(c.text)

    return output_list




    
def  action_syslog(msg,  priority="6",facility="MLANG"):

    """

       For sending a syslog message from EEM python script 
            e.g  action_syslog ("Interface is down", "6","EEM")


    Args:  

          msg              :  Syslog Message

          priority         :  Priority of the syslog message
                              Supported values are, 
                               a) emerg|alert|crit|err|warning|notice|info|debug
                               b) "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7"

          facility         :  Facility string to be used in the syslog message.

    Returns:
          Status Output (if is success)
          Raise an exception with the appropriate message(if there is a failure)
                                  
    """
    if EEM_DATA_FORMAT == 1 :
        EEM_ACTION_SYSLOG_STMT = """\
                <?xml>
                <eemType>ACTION</eemType>
                <reqType>action_syslog</reqType>
                <msg>{msg}</msg>
            """.format(msg=_eem_encode_base64(msg))
    

        if len(str(priority).strip()) > 0 :
            EEM_ACTION_SYSLOG_STMT = EEM_ACTION_SYSLOG_STMT + """\
                <priority>{priority}</priority>
                """.format(priority=_eem_encode_base64(str(priority)))
            
        else:
            EEM_ACTION_SYSLOG_STMT = EEM_ACTION_SYSLOG_STMT + """\
                <priority>{priority}</priority>
                """.format(priority=_eem_encode_base64("6"))
            


        if len(facility.strip()) > 0 :
            EEM_ACTION_SYSLOG_STMT = EEM_ACTION_SYSLOG_STMT + """\
                <facility>{facility}</facility>
                """.format(facility=_eem_encode_base64(facility))

        else:
            EEM_ACTION_SYSLOG_STMT = EEM_ACTION_SYSLOG_STMT + """\
                <facility>{facility}</facility>
                """.format(facility=_eem_encode_base64("EEM"))
    # Added code START ----------------------------
    command = EEM_ACTION_SYSLOG_STMT;
    #print("command being sent in enc format : ", _eem_encode_base64(command), ":\n")
    # Use iosp_client
    try:
        iosp_client_output = subprocess.check_output("iosp_client -t 10 -om 1 -f eem_proxy 1 " + _eem_encode_base64(command), stderr=subprocess.STDOUT, shell=True).decode()
        command_status = get_command_response(iosp_client_output, 1)
        return command_status[2]
    except subprocess.CalledProcessError as iosp_client_error:
        #print ("error code ", iosp_client_error.returncode, " ", iosp_client_error.output.decode())
        raise Exception(iosp_client_error.output.decode())
    # print("output being returned : ",iosp_client_output,"\n")
    # Added code END ------------------------------

    

def action_reload():

    """
       For reloading the device using EEM Action.

       Args:  None

       Returns:
          Status Output (if is success)
          Raise an exception with the appropriate message(if there is a failure)

    """
  
    if EEM_DATA_FORMAT == 1 :
        EEM_ACTION_RELOAD_STMT = """\
        <?xml>
        <eemType>ACTION</eemType>
        <reqType>action_reload</reqType>                
        """
    command = EEM_ACTION_RELOAD_STMT;
    try:
        iosp_client_output = subprocess.check_output("iosp_client -t 10 -om 1 -f eem_proxy 1 " + _eem_encode_base64(command), stderr=subprocess.STDOUT, shell=True).decode()
        command_status = get_command_response(iosp_client_output, 1)
        return command_status[2]
    except subprocess.CalledProcessError as iosp_client_error:
        raise Exception(iosp_client_error.output.decode())



def action_switch():

    """
       To perform switchover to standby supervisor(if available) using EEM Action.

       Args:  None

       Returns:
          Status Output (if is success)
          Raise an exception with the appropriate message(if there is a failure)

    """
  
    if EEM_DATA_FORMAT == 1 :
        EEM_ACTION_SWITCH_STMT = """\
                <?xml>
                <eemType>ACTION</eemType>
                <reqType>action_switch</reqType>                
            """
    command = EEM_ACTION_SWITCH_STMT;
    try:
        iosp_client_output = subprocess.check_output("iosp_client -t 10 -om 1 -f eem_proxy 1 " + _eem_encode_base64(command), stderr=subprocess.STDOUT, shell=True).decode()
        command_status = get_command_response(iosp_client_output, 1)
        return  command_status[2]
    except subprocess.CalledProcessError as iosp_client_error:
        raise Exception(iosp_client_error.output.decode())




def action_track_read(track_number):

    """
       Returns the status of the given track number. 

       Args:
         
            track_number       :   Track number for which the status needs to be returned


       Returns:
            Return the Status of the track object identified by 'Track number' 
            Raise an exception with the appropriate message(if there is a failure)

    """
 
    if EEM_DATA_FORMAT == 1 :
        if len(str(track_number).strip()) > 0 :
            EEM_ACTION_POLICY_STMT = """\
                <?xml>
                <eemType>ACTION</eemType>
                <reqType>action_track_read</reqType>
                <number>{track_number}</number>
            """.format(track_number=_eem_encode_base64(str(track_number)))
        else:
            raise Exception("Track name cannot be null / empty string")
    command = EEM_ACTION_POLICY_STMT;
    try:
        iosp_client_output = subprocess.check_output("iosp_client -t 10 -om 1 -f eem_proxy 1 " + _eem_encode_base64(command), stderr=subprocess.STDOUT, shell=True).decode()
        command_status = get_command_response(iosp_client_output, 1)
        return  command_status[2]
    except subprocess.CalledProcessError as iosp_client_error:
        raise Exception(iosp_client_error.output.decode())



def action_track_set(track_number, state):

    """
       Sets the status of the given track number.

       Args:

            track_number       :   Track number for which the status needs to be set 
 
            state              :   State of the track to be set. 
                                   Supported values are 
                                           up | down

       Returns:
            Status of the queried track object(if is success)
            Raise an exception with the appropriate message(if there is a failure)

    """


    if EEM_DATA_FORMAT == 1 :
        if len(str(track_number).strip()) > 0 and len(str(state).strip()) > 0 :
            EEM_ACTION_POLICY_STMT = """\
                    <?xml>
                <eemType>ACTION</eemType>
                <reqType>action_track_set</reqType>
                <number>{track_number}</number>
                <state>{state}</state>
                """.format(track_number=_eem_encode_base64(str(track_number)),
                        state=_eem_encode_base64(state))
        else:
            raise Exception("Track name/state cannot be null / empty string")
    command = EEM_ACTION_POLICY_STMT;
    try:
        iosp_client_output = subprocess.check_output("iosp_client -t 10 -om 1 -f eem_proxy 1 " + _eem_encode_base64(command), stderr=subprocess.STDOUT, shell=True).decode()
        command_status = get_command_response(iosp_client_output, 1)
        if command_status[0] == 'success' :
            return  command_status[2]
        else:
            raise Exception(command_status[2])
    except subprocess.CalledProcessError as iosp_client_error:
        raise Exception(iosp_client_error.output.decode())



def cli_run( commands) :


    """
       Runs the list of CLIs given in the parameter. 

       Args:

          Commands  :  List of commands to be executed
               if the argument 'commands' needs to be 
                  i) Python list type that contains 
                         list of commands
                  ii) Single command like "show version"
                
                  Eg
                          cmds = [ 'show ver' , 'show clock']
                          cli_run(cmds)
                  OR
                          cmd = "show version"
                          cli_run(cmd)
                                  
          Returns  :  Two List 
                      i) Command Status 
                      ii) Command output. 

    """

    command_status = []
    command_output = []

    if isinstance(commands, list) :
        EEM_CLI_RUN_STMT = """\
        <?xml>
        <eemType>CLI</eemType>
        <reqType>cli_run</reqType>
        """
        i = 1   
        for item in commands :  
            EEM_CLI_RUN_STMT = EEM_CLI_RUN_STMT + \
                    """<cmd{i}>{cmd}</cmd{i}>
            """.format(i=i,cmd=_eem_encode_base64(item))
            i +=  1
    else :
        EEM_CLI_RUN_STMT = """\
        <?xml>
        <eemType>CLI</eemType>
        <reqType>cli_run</reqType>
        <cmd1>{cmd}</cmd1>
        """.format(cmd=_eem_encode_base64(commands))

    command = EEM_CLI_RUN_STMT;
    try:
        iosp_client_output = subprocess.check_output("iosp_client -t 10 -om 1 -f eem_proxy 1 " + _eem_encode_base64(command), stderr=subprocess.STDOUT, shell=True).decode()
        command_status, command_output = get_command_response(iosp_client_output, 2)
        if command_status[0] == 'success' :
            return command_output
        else:
            raise Exception( command_status[2])
    except subprocess.CalledProcessError as iosp_client_error:
        raise Exception(iosp_client_error.output.decode())



def cli_open() :

 
    """
       Opens a vty and returns the vty handle to be used for subsequent requests.
              E.g  fd = cli_open()

       Args:     None
       
       Returns:
           Newly opened Vty handle (if is success)
           Raise an exception with the appropriate message(if it is a failure)

    """

    command_status = []

    EEM_CLI_OPEN_STMT = """\
    <?xml>
    <eemType>CLI</eemType>
    <reqType>cli_open</reqType>
     """

    command = EEM_CLI_OPEN_STMT;
    try:
        iosp_client_output = subprocess.check_output("iosp_client -t 10 -om 1 -f eem_proxy 1 " + _eem_encode_base64(command), stderr=subprocess.STDOUT, shell=True).decode()
        command_status = get_command_response(iosp_client_output, 1)
        if command_status[0] == 'success' :
            return command_status[2]
        else:
            raise Exception( command_status[2])
    except subprocess.CalledProcessError as iosp_client_error:
        raise Exception(iosp_client_error.output.decode())






def cli_close(fd) :

    """
      Closes the given vty 

      Args:     

           fd        :      VTY that needs to be closed.

       Returns:
           Status of close operation (if is success)
           Raise an exception with the appropriate message(if it is a failure)


    """
    command_status = []

    EEM_CLI_CLOSE_STMT = """\
    <?xml>
    <eemType>CLI</eemType>
    <reqType>cli_close</reqType>
    <fd>{fd}</fd>
    """.format(fd=_eem_encode_base64(fd))

    command = EEM_CLI_CLOSE_STMT;
    try:
        iosp_client_output = subprocess.check_output("iosp_client -t 10 -om 1 -f eem_proxy 1 " + _eem_encode_base64(command), stderr=subprocess.STDOUT, shell=True).decode()
        command_status = get_command_response(iosp_client_output, 1)
        if command_status[0] == 'success' :
            return command_status[2]
        else:
            raise Exception( command_status[2])
    except subprocess.CalledProcessError as iosp_client_error:
        raise Exception(iosp_client_error.output.decode())

    

def cli_exec( fd , cmd ) :

    """
      Execute the given command on the vty handle given in the parameter 

      Args:

           fd        :      VTY on that the command needs to be executed
   
           cmd       :      Command that needs to be executed

      Returns:
           Returns the command output (if is success)   
           Raise an exception with the appropriate message(if is failure)


    """

    command_status = []

    EEM_CLI_EXEC_STMT = """\
    <?xml>
    <eemType>CLI</eemType>
    <reqType>cli_exec</reqType>
    <fd>{fd}</fd>
    <cmd>{cmd}</cmd>
    """.format(fd=_eem_encode_base64(fd),cmd=_eem_encode_base64(cmd))

    command = EEM_CLI_EXEC_STMT;
    try:
        iosp_client_output = subprocess.check_output("iosp_client -t 10 -om 1 -f eem_proxy 1 " + _eem_encode_base64(command), stderr=subprocess.STDOUT, shell=True).decode()
        command_status = get_command_response(iosp_client_output, 1)
        if command_status[0] == 'success' :
            return command_status[2]
        else:
            raise Exception( command_status[2])
    except subprocess.CalledProcessError as iosp_client_error:
        raise Exception(iosp_client_error.output.decode())




def cli_get_ttyname(fd) :

    """
      Get the vty name for the given vty handle

      Args:

           fd        :      VTY handle for which the name needs to be returned

      Returns:
           Vty name (if is success)
           Raise an exception with the appropriate message(if there is a failure)


    """

    EEM_CLI_GET_TTY_NAME_STMT = """\
      <?xml>
      <eemType>CLI</eemType>
      <reqType>cli_get_ttyname</reqType>
      <fd>{fd}</fd>
      """.format(fd=_eem_encode_base64(fd))

    command = EEM_CLI_GET_TTY_NAME_STMT;
    try:
        iosp_client_output = subprocess.check_output("iosp_client -t 10 -om 1 -f eem_proxy 1 " + _eem_encode_base64(command), stderr=subprocess.STDOUT, shell=True).decode()
        command_status = get_command_response(iosp_client_output, 1)
        if command_status[0] == 'success' :
            return command_status[2]
        else:
            raise Exception( command_status[2])
    except subprocess.CalledProcessError as iosp_client_error:
        raise Exception(iosp_client_error.output.decode())




def cli_read(fd) :

    """
      Read the command output from the given vty 

      Args:

           fd        :      VTY handle from which read the command output

      Returns:
           Command Output (if is success)
           Raise an exception with the appropriate message(if it is a failure)


    """

    command_status = []

    EEM_CLI_READ_STMT = """\
      <?xml>
      <eemType>CLI</eemType>
      <reqType>cli_read</reqType>
      <fd>{fd}</fd>
      """.format(fd=_eem_encode_base64(fd))

    command = EEM_CLI_READ_STMT;
    try:
        iosp_client_output = subprocess.check_output("iosp_client -t 10 -om 1 -f eem_proxy 1 " + _eem_encode_base64(command), stderr=subprocess.STDOUT, shell=True).decode()
        command_status = get_command_response(iosp_client_output, 1)
        if command_status[0] == 'success' :
            return command_status[2]
        else:
            raise Exception( command_status[2])
    except subprocess.CalledProcessError as iosp_client_error:
        raise Exception(iosp_client_error.output.decode())




def cli_read_line(fd) :
    """
      Read single line command output from the given vty

      Args:

           fd        :      VTY handle from which read the command output

      Returns:
           One line of Command Output (if is success)
           Raise an exception with the appropriate message(if it is a failure)


    """
 
    command_status = []
 
    EEM_CLI_READ_LINE_STMT = """\
      <?xml>
      <eemType>CLI</eemType>
      <reqType>cli_read_line</reqType>
      <fd>{fd}</fd>
      """.format(fd=_eem_encode_base64(fd))


    command = EEM_CLI_READ_LINE_STMT;
    try:
        iosp_client_output = subprocess.check_output("iosp_client -t 10 -om 1 -f eem_proxy 1 " + _eem_encode_base64(command), stderr=subprocess.STDOUT, shell=True).decode()
        command_status = get_command_response(iosp_client_output, 1)
        if command_status[0] == 'success' :
            return command_status[2]
        else:
            raise Exception( command_status[2])
    except subprocess.CalledProcessError as iosp_client_error:
        raise Exception(iosp_client_error.output.decode())
  


def cli_read_drain(fd, duration=200) :

    """
      Read command output from the given vty for the given duration and it will not wait for host prompt to appear.

      Args:

           fd        :      VTY handle from which read the command output
           duration  :      Duration to wait to collec the data from channel

      Returns:
           Command Output (if is success)
           Raise an exception with the appropriate message(if it is a failure)

    """

    command_status = []

    EEM_CLI_READ_DRAIN_STMT = """\
      <?xml>
      <eemType>CLI</eemType>
      <reqType>cli_read_drain</reqType>
      <fd>{fd}</fd>
      <duration>{d}</duration>
      """.format(fd=_eem_encode_base64(fd),d=_eem_encode_base64(duration))

    command = EEM_CLI_READ_DRAIN_STMT;
    try:
        iosp_client_output = subprocess.check_output("iosp_client -t 10 -om 1 -f eem_proxy 1 " + _eem_encode_base64(command), stderr=subprocess.STDOUT, shell=True).decode()
        command_status = get_command_response(iosp_client_output, 1)
        if command_status[0] == 'success' :
            return command_status[2]
        else:
            raise Exception( command_status[2])
    except subprocess.CalledProcessError as iosp_client_error:
        raise Exception(iosp_client_error.output.decode())




def cli_read_pattern(fd,pattern) :

    """
      Read command output from the given vty until the given pattern occurs.

      Args:

           fd        :      VTY handle from which read the command output until the pattern occurs

      Returns:
           Command Output (if is success)
           Raise an exception with the appropriate message(if it is a failure)

    """


    command_status =  []

    EEM_CLI_READ_PATTERN_STMT = """\
       <?xml>
       <eemType>CLI</eemType>
       <reqType>cli_read_pattern</reqType>
       <fd>{fd}</fd>
       <cmd>{pattern}</cmd>
       """.format(fd=_eem_encode_base64(fd),pattern=_eem_encode_base64(pattern))


    command = EEM_CLI_READ_PATTERN_STMT;
    try:
        iosp_client_output = subprocess.check_output("iosp_client -t 10 -om 1 -f eem_proxy 1 " + _eem_encode_base64(command), stderr=subprocess.STDOUT, shell=True).decode()
        command_status = get_command_response(iosp_client_output, 1)
        if command_status[0] == 'success' :
            return command_status[2]
        else:
            raise Exception( command_status[2])
    except subprocess.CalledProcessError as iosp_client_error:
        raise Exception(iosp_client_error.output.decode())




def cli_write(fd,cmd) :

    """
      Write the given command on the given vty 

      Args:

           fd        :      VTY handle on that the command needs to be executed

           cmd       :      Command that needs to be executed

      Returns:
           Status of the command execution (if is success)
           Raise an exception with the appropriate message(if it is a failure)

    """

    command_status = []

    EEM_CLI_WRITE_STMT = """\
       <?xml>
       <eemType>CLI</eemType>
       <reqType>cli_write</reqType>
       <fd>{fd}</fd>
       <cmd>{cmd}</cmd>
       """.format(fd=_eem_encode_base64(fd),cmd=_eem_encode_base64(cmd))

    command = EEM_CLI_WRITE_STMT;
    try:
        iosp_client_output = subprocess.check_output("iosp_client -t 10 -om 1 -f eem_proxy 1 " + _eem_encode_base64(command), stderr=subprocess.STDOUT, shell=True).decode()
        command_status = get_command_response(iosp_client_output, 1)
        if command_status[0] == 'success' :
            return command_status[2]
        else:
            raise Exception( command_status[2])
    except subprocess.CalledProcessError as iosp_client_error:
        raise Exception(iosp_client_error.output.decode())



def cli_run_interactive(commands) :

    """
      Execute interactive commands given in the commands list

      Args:

        commands   :  Command that needs to be executed.
                      It should be a python list or list of lists &
                      each list item should be of the below format
                      E.g.
                      l = [ 'cmd' , 'expect' , 'reply']
                      OR
                      l = [['cmd', 'expect' , 'reply', 'expect', 'reply'...], ['cmd', 'expect' , 'reply', 'expect', 'reply'...], ...]

      Returns:
           Status of the command execution (if is success)
           Raise an exception with the appropriate message(if is a failure)

    """

    command_status = []
    command_output = []

    if isinstance(commands, list) or all(isinstance(s, list) for s in commands) :
        EEM_CLI_RUN_INT_STMT = """\
                <?xml>
                <eemType>CLI</eemType>
                <reqType>cli_run_interactive</reqType>
                """
        if all(isinstance(k, list) for k in commands):
            ''' This is for list of lists. [[abcdef][xyz]]'''
            i = 1
            for list_cur in commands:
                EEM_CLI_RUN_INT_STMT = EEM_CLI_RUN_INT_STMT + \
                                     """<cmd{i}>""".format(i=i)

                if len(list_cur) > 2 :
                    test_count =  (len(list_cur) - 1) % 2
                    if test_count != 0 :
                        raise Exception("Incorrect format of input. Please refer help.\
                                        \n Sample : [['a', 'b', 'c', 'd', 'e', 'f']['x', 'y', 'z']]")
                    else:
                        EEM_CLI_RUN_INT_STMT = EEM_CLI_RUN_INT_STMT + \
                        """<cmd>{cmd}</cmd>""".format(cmd=_eem_encode_base64(list_cur[0]))

                        for j in range(1,len(list_cur),2):
                            EEM_CLI_RUN_INT_STMT = EEM_CLI_RUN_INT_STMT + \
                                              """<exp>{exp}</exp>
                                                 <rep>{rep}</rep>
                                 """.format(exp=_eem_encode_base64(list_cur[j]),
                                 rep=_eem_encode_base64(list_cur[j+1]))

                        EEM_CLI_RUN_INT_STMT = EEM_CLI_RUN_INT_STMT + \
                                           """</cmd{i}>""".format(i=i)
                i += 1
        else:
            ''' This is for single list : [abcdef]'''
            if len(commands) > 2:
                test_count = (len(commands) - 1) % 2
                if test_count != 0:
                    raise Exception("Incorrect format of input. Please refer help. \
                                    \n Sample : ['a', 'b', 'c', 'd', 'e', 'f']")
                else:
                    EEM_CLI_RUN_INT_STMT = EEM_CLI_RUN_INT_STMT + \
                                         """<cmd1>"""

                    EEM_CLI_RUN_INT_STMT = EEM_CLI_RUN_INT_STMT + \
                        """<cmd>{cmd}</cmd>""".format(cmd=_eem_encode_base64(commands[0]))

                    for j in range(1, len(commands), 2):
                        EEM_CLI_RUN_INT_STMT = EEM_CLI_RUN_INT_STMT + \
                                                  """<exp>{exp}</exp>
                                                     <rep>{rep}</rep>
                                     """.format(exp=_eem_encode_base64(commands[j]),
                                     rep=_eem_encode_base64(commands[j+1]))

                    EEM_CLI_RUN_INT_STMT = EEM_CLI_RUN_INT_STMT + \
                                               """</cmd1>"""

        command = EEM_CLI_RUN_INT_STMT
        # print("command formed at end : ", command)
        try:
            iosp_client_output = subprocess.check_output("iosp_client -t 10 -om 1 -f eem_proxy 1 " + _eem_encode_base64(command), stderr=subprocess.STDOUT, shell=True).decode()
            command_status, command_output = get_command_response(iosp_client_output, 2)
            if command_status[0] == 'success':
                return command_output
            else:
                raise Exception(command_status[2])
        except subprocess.CalledProcessError as iosp_client_error:
            raise Exception(iosp_client_error.output.decode())
    else:
        raise Exception( "cli_run input should be 'list' or list of list")




def event_publish(sub_system, type , arg1=None, arg2=None,arg3=None,arg4=None) :

    """
      Publish application event 

      Args:

           sub_system    :      Subsystem id 
           type          :      Sub Type 
           arg1          :      Send arguments along with publish(optional)
           arg2          :      Send arguments along with publish(optional)
           arg3          :      Send arguments along with publish(optional)
           arg4          :      Send arguments along with publish(optional)

      Returns:
           Status Output (if is success)
           Raise an exception with the appropriate message(if is a failure)

    """
   
    command_status = []
    command_output = []

    EEM_EVENT_PUBLISH_STMT = """\
                <?xml>
                <eemType>event</eemType>
                <reqType>event_publish</reqType> 
                <sub_system>{sub_system}</sub_system>
                <type>{type}</type>
                """.format(sub_system=_eem_encode_base64(str(sub_system)),
                           type=_eem_encode_base64(str(type)))


    if arg1 is not None :
        EEM_EVENT_PUBLISH_STMT = EEM_EVENT_PUBLISH_STMT + \
                                 """<arg1>{arg1}</arg1>""".format(arg1=_eem_encode_base64(arg1))

    if arg2 is not None :
        EEM_EVENT_PUBLISH_STMT = EEM_EVENT_PUBLISH_STMT + \
                                 """<arg2>{arg2}</arg2>""".format(arg2=_eem_encode_base64(arg2))
                 
 
    if arg3 is not None :
        EEM_EVENT_PUBLISH_STMT = EEM_EVENT_PUBLISH_STMT + \
                                 """<arg3>{arg3}</arg3>""".format(arg3=_eem_encode_base64(arg3))
                  

    if arg4 is not None :
        EEM_EVENT_PUBLISH_STMT = EEM_EVENT_PUBLISH_STMT + \
                                 """<arg4>{arg4}</arg4>""".format(arg4=_eem_encode_base64(arg4))
                  


    command = EEM_EVENT_PUBLISH_STMT;
    try:
        iosp_client_output = subprocess.check_output("iosp_client -t 10 -om 1 -f eem_proxy 1 " + _eem_encode_base64(command), stderr=subprocess.STDOUT, shell=True).decode()
        command_status,command_output = get_command_response(iosp_client_output,2)
        if command_status[0] == 'success' :
            return command_status
        else:
            raise Exception( command_status[2])
    except subprocess.CalledProcessError as iosp_client_error:
        raise Exception(iosp_client_error.output.decode())



def event_reqinfo() :

    """
      Gets the event information pertaining to the current event.

      Args:    None

      Returns:
          Python Dictionary  (if is success)
           Format is { 'Event Tag' , {_event_var1 : value1, event_var2: value2, ...} }

           Raise an exception with the appropriate message(if it is a failure)

    """
    global EEM_BUILTIN


    if EEM_BUILTIN == None: 
        command_status = []
        command_output = []

        EEM_EVENT_REQINFO_STMT = """\
                <?xml>
                <eemType>ENV</eemType>
                <reqType>env_built_in</reqType>
                """

        command = EEM_EVENT_REQINFO_STMT;
        try:
            iosp_client_output = subprocess.check_output("iosp_client -t 10 -om 1 -f eem_proxy 1 " + _eem_encode_base64(command), stderr=subprocess.STDOUT, shell=True).decode()
            command_status = get_env_response(iosp_client_output,1)
            EEM_BUILTIN = command_status
            #print("EEM_BUILTIN : ", EEM_BUILTIN)
        except subprocess.CalledProcessError as iosp_client_error:
            raise Exception(iosp_client_error.output.decode())

    else:
        command_status = EEM_BUILTIN

    return command_status




def event_reqinfo_multi() :

    """
      Gets the multi event information pertaining to the current event.

      Args:    None

      Returns:
           Python Dictionary  (if is success)
               Format is { 
                          'Event Tag1' , {_event_var1 : value, event_var2: value2, ...} 
                          'Event Tag2' , {_event_var1 : value, event_var2: value2, ...} 
                           .
                           .
                         }

           Raise an exception with the appropriate message(if there is a failure)

    """
    global EEM_BUILTIN_MULTI


    if EEM_BUILTIN_MULTI == None:

        command_status = []
        command_output = []

        EEM_EVENT_REQINFO_STMT = """\
                <?xml>
                <eemType>ENV</eemType>
                <reqType>env_built_in_multi</reqType>
                """
        command = EEM_EVENT_REQINFO_STMT;
        try:
            iosp_client_output = subprocess.check_output(
                "iosp_client -t 10 -om 1 -f eem_proxy 1 " + _eem_encode_base64(command), stderr=subprocess.STDOUT, shell=True).decode()
            command_status = get_env_response(iosp_client_output,2)
            EEM_BUILTIN_MULTI = command_status
            #print("EEM_BUILTIN_MULTI : ", EEM_BUILTIN_MULTI)
        except subprocess.CalledProcessError as iosp_client_error:
            raise Exception(iosp_client_error.output.decode())


    else:
        command_status = EEM_BUILTIN_MULTI

    return command_status




def  env_reqinfo() :


    """
      Gets the user defined EEM Environment variables 

      Args:    None

      Returns:
           Python Dictionary  (if is success)
               Format is { _user_var1 : value, user_var2: value2, ... }

           Raise an exception with the appropriate message(if there is a failure)

    """
    global EEM_USER_VARIABLES

    if EEM_USER_VARIABLES == None :
        command_status = []
        command_output = []

        EEM_ENV_USER_VARS_STMT = """\
                <?xml>
        <eemType>ENV</eemType>
        <reqType>env_user</reqType>
                """
        command = EEM_ENV_USER_VARS_STMT;
        try:
            iosp_client_output = subprocess.check_output(
                "iosp_client -t 10 -om 1 -f eem_proxy 1 " + _eem_encode_base64(command), stderr=subprocess.STDOUT, shell=True).decode()
            command_status = get_user_response(iosp_client_output,1)
            EEM_USER_VARIABLES = command_status
            #print("EEM_USER_VARIABLES : ", EEM_USER_VARIABLES)
        except subprocess.CalledProcessError as iosp_client_error:
            raise Exception(iosp_client_error.output.decode())

    else:
        command_status = EEM_USER_VARIABLES 


    return command_status


def get_env_var(env_variable_name):
    """
    Function to retrieve the EEM environment  variables that are defined by
    user using 'event manager environment <var> <value> 
    For example, 
                 
    If the user has defined a variable called 'MAILTO' using
        event manager environment MAILTO "cs-eem@cisco.com"
                 
        Using below function, user can retrieve the value of the 
        'MAILTO' variable and mail_id variable will have 
        'cs-cisco@cisco.com'
                 
        mail_id = get_env_var("MAILTO") 

    Args:

          env_variable_name      :      User defined EEM Environment variable
          
    Returns:
          Value of the variable indicated by 'env_variable_name' (if is success)
          None (if there is no such variable)

    """    
    global EEM_USER_VARIABLES
    
    if EEM_USER_VARIABLES != None:
        if env_variable_name.encode() in EEM_USER_VARIABLES :
            return(EEM_USER_VARIABLES[env_variable_name.encode()].decode())
        else:
            return None
              
    else:
        env_reqinfo()
        if env_variable_name.encode() in EEM_USER_VARIABLES :
            return(EEM_USER_VARIABLES[env_variable_name.encode()].decode())
        else:
            return None
 

def get_event_var(event_variable_name):
    """
    Function to retrieve the event variables that are populated as part of event publish 
    For example, 
       get_event_var("msg") for syslog would return the built-in event variable of syslog message

     Args:

          event_variable_name      :      Event variable for which the value needs to be returned
          
     Returns:
          Value of the variable indicated by 'event_variable_name' (if is success)
          None (if there is no such variable)

    """
    global EEM_BUILTIN

    if EEM_BUILTIN != None:
        if event_variable_name.encode() in EEM_BUILTIN :
            return(EEM_BUILTIN[event_variable_name.encode()].decode())
        else:
            return None

    else:
        event_reqinfo() 
        if event_variable_name.encode() in EEM_BUILTIN :
            return(EEM_BUILTIN[event_variable_name.encode()].decode())
        else:
            return None




def action_snmp_trap( intdata1 = None , intdata2 = None, strdata = None) :

    """
     Sends an SNMP Trap 

     Args:

          intdata1      :      Optional parameter to accept integer value
          intdata2      :      Optional parameter to accept integer value
          strdata       :      Optional parameter to send string value

     Returns:
          Status Output (if is success)
          Raise an exception with the appropriate message(if there is a failure)

    """

    command_status = []

    EEM_ACTION_SNMP_TRAP_STMT = """\
        <?xml>
        <eemType>ACTION</eemType>
        <reqType>action_snmp_trap</reqType>
        """

    if intdata1 != None :
        EEM_ACTION_SNMP_TRAP_STMT = EEM_ACTION_SNMP_TRAP_STMT + \
               """<intdata1>{d1}</intdata1>""".format \
                          (d1=_eem_encode_base64(str(intdata1)))

    if intdata1 != None :
        EEM_ACTION_SNMP_TRAP_STMT = EEM_ACTION_SNMP_TRAP_STMT + \
               """<intdata2>{d2}</intdata2>""".format \
                          (d2=_eem_encode_base64(str(intdata2)))

    if strdata != None :
        EEM_ACTION_SNMP_TRAP_STMT = EEM_ACTION_SNMP_TRAP_STMT + \
               """<strdata>{d3}</strdata>""".format \
                          (d3=_eem_encode_base64(str(strdata)))

    command = EEM_ACTION_SNMP_TRAP_STMT;
    try:
        iosp_client_output = subprocess.check_output("iosp_client -t 10 -om 1 -f eem_proxy 1 " + _eem_encode_base64(command), stderr=subprocess.STDOUT, shell=True).decode()
        command_status = get_command_response(iosp_client_output, 1)
        if command_status[0] == 'success' :
            return command_status[2]
        else:
            raise Exception( command_status[2])
    except subprocess.CalledProcessError as iosp_client_error:
        raise Exception(iosp_client_error.output.decode())





def action_export_to_telemetry( arg1 = None , arg2 = None, arg3 = None, arg4 = None, arg5 = None) :

    """
     Sends a notification to Telemetry

     Args:

          arg1      :      Optional parameter to send user/builtin variable
          arg2      :      Optional parameter to send user/builtin variable
          arg3      :      Optional parameter to send user/builtin variable
          arg4      :      Optional parameter to send user/builtin variable
          arg5      :      Optional parameter to send user/builtin variable
          

     Returns:
          Status Output (if is success)
          Raise an exception with the appropriate message(if there is a failure)

    """

    command_status = []

    EEM_ACTION_EXPORT_TELEMETRY_STMT = """\
        <?xml>
        <eemType>ACTION</eemType>
        <reqType>action_export_to_telemetry</reqType>
        """

    if arg1 != None :
        if get_event_var(str(arg1)) != None:
            EEM_ACTION_EXPORT_TELEMETRY_STMT = EEM_ACTION_EXPORT_TELEMETRY_STMT + \
                   """<name1>{n1}</name1>""".format \
                           (n1=_eem_encode_base64(str(arg1)))
            EEM_ACTION_EXPORT_TELEMETRY_STMT = EEM_ACTION_EXPORT_TELEMETRY_STMT + \
                   """<value1>{v1}</value1>""".format \
                              (v1=_eem_encode_base64(str(get_event_var(arg1))))
        else :
            if get_env_var(str(arg1)) != None:
                EEM_ACTION_EXPORT_TELEMETRY_STMT = EEM_ACTION_EXPORT_TELEMETRY_STMT + \
                       """<name1>{n1}</name1>""".format \
                                  (n1=_eem_encode_base64(str(arg1)))
                EEM_ACTION_EXPORT_TELEMETRY_STMT = EEM_ACTION_EXPORT_TELEMETRY_STMT + \
                       """<value1>{v1}</value1>""".format \
                                  (v1=_eem_encode_base64(str(get_env_var(arg1))))
            else :
                raise Exception() 

    if arg2 != None :
        if get_event_var(str(arg2)) != None:
            EEM_ACTION_EXPORT_TELEMETRY_STMT = EEM_ACTION_EXPORT_TELEMETRY_STMT + \
                   """<name2>{n2}</name2>""".format \
                              (n2=_eem_encode_base64(str(arg2)))
            EEM_ACTION_EXPORT_TELEMETRY_STMT = EEM_ACTION_EXPORT_TELEMETRY_STMT + \
                   """<value2>{v2}</value2>""".format \
                              (v2=_eem_encode_base64(str(get_event_var(arg2))))
        else :
            if get_env_var(str(arg2)) != None:
                EEM_ACTION_EXPORT_TELEMETRY_STMT = EEM_ACTION_EXPORT_TELEMETRY_STMT + \
                       """<name2>{n2}</name2>""".format \
                                  (n2=_eem_encode_base64(str(arg2)))
                EEM_ACTION_EXPORT_TELEMETRY_STMT = EEM_ACTION_EXPORT_TELEMETRY_STMT + \
                       """<value2>{v2}</value2>""".format \
                                  (v2=_eem_encode_base64(str(get_env_var(arg2))))
            else :
                raise Exception()

    if arg3 != None :
        if get_event_var(str(arg3)) != None:
            EEM_ACTION_EXPORT_TELEMETRY_STMT = EEM_ACTION_EXPORT_TELEMETRY_STMT + \
                   """<name3>{n3}</name3>""".format \
                              (n3=_eem_encode_base64(str(arg3)))
            EEM_ACTION_EXPORT_TELEMETRY_STMT = EEM_ACTION_EXPORT_TELEMETRY_STMT + \
                   """<value3>{v3}</value3>""".format \
                              (v3=_eem_encode_base64(str(get_event_var(arg3))))
        else :
            if get_env_var(str(arg3)) != None:
                EEM_ACTION_EXPORT_TELEMETRY_STMT = EEM_ACTION_EXPORT_TELEMETRY_STMT + \
                       """<name3>{n3}</name3>""".format \
                                  (n3=_eem_encode_base64(str(arg3)))
                EEM_ACTION_EXPORT_TELEMETRY_STMT = EEM_ACTION_EXPORT_TELEMETRY_STMT + \
                       """<value3>{v3}</value3>""".format \
                                  (v3=_eem_encode_base64(str(get_env_var(arg3))))
            else :
                raise Exception()

    if arg4 != None :
        if get_event_var(str(arg4)) != None:
            EEM_ACTION_EXPORT_TELEMETRY_STMT = EEM_ACTION_EXPORT_TELEMETRY_STMT + \
                   """<name4>{n4}</name4>""".format \
                              (n4=_eem_encode_base64(str(arg4)))
            EEM_ACTION_EXPORT_TELEMETRY_STMT = EEM_ACTION_EXPORT_TELEMETRY_STMT + \
                   """<value4>{v4}</value4>""".format \
                              (v4=_eem_encode_base64(str(get_event_var(arg4))))
        else :
            if get_env_var(str(arg4)) != None:
                EEM_ACTION_EXPORT_TELEMETRY_STMT = EEM_ACTION_EXPORT_TELEMETRY_STMT + \
                       """<name4>{n4}</name4>""".format \
                                  (n4=_eem_encode_base64(str(arg4)))
                EEM_ACTION_EXPORT_TELEMETRY_STMT = EEM_ACTION_EXPORT_TELEMETRY_STMT + \
                       """<value4>{v4}</value4>""".format \
                                  (v4=_eem_encode_base64(str(get_env_var(arg4))))
            else :
                raise Exception()

    if arg5 != None :
        if get_event_var(str(arg5)) != None:
            EEM_ACTION_EXPORT_TELEMETRY_STMT = EEM_ACTION_EXPORT_TELEMETRY_STMT + \
                   """<name5>{n5}</name5>""".format \
                              (n5=_eem_encode_base64(str(arg5)))
            EEM_ACTION_EXPORT_TELEMETRY_STMT = EEM_ACTION_EXPORT_TELEMETRY_STMT + \
                   """<value5>{v5}</value5>""".format \
                              (v5=_eem_encode_base64(str(get_event_var(arg5))))
        else :
            if get_env_var(str(arg5)) != None:
                EEM_ACTION_EXPORT_TELEMETRY_STMT = EEM_ACTION_EXPORT_TELEMETRY_STMT + \
                       """<name5>{n5}</name5>""".format \
                                  (n5=_eem_encode_base64(str(arg5)))
                EEM_ACTION_EXPORT_TELEMETRY_STMT = EEM_ACTION_EXPORT_TELEMETRY_STMT + \
                       """<value5>{v5}</value5>""".format \
                                  (v5=_eem_encode_base64(str(get_env_var(arg5))))
            else :
                raise Exception()

    command = EEM_ACTION_EXPORT_TELEMETRY_STMT;
    try:
        iosp_client_output = subprocess.check_output("iosp_client -t 10 -om 1 -f eem_proxy 1 " + _eem_encode_base64(command), stderr=subprocess.STDOUT, shell=True).decode()
        command_status = get_command_response(iosp_client_output, 1)
        if command_status[0] == 'success' :
            return command_status[2]
        else:
            raise Exception( command_status[2])
    except subprocess.CalledProcessError as iosp_client_error:
        raise Exception(iosp_client_error.output.decode())
