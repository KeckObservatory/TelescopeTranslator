from ddoitranslatormodule.ddoiexceptions.DDOIExceptions import DDOIKTLTimeOut
from telescopetranslator.BaseTelescope import TelescopeBase

import ktl
from collections import OrderedDict


class MoveTelescopeFocus(TelescopeBase):
    """
    telfoc -- set/show the telescope secondary position

     SYNOPSIS
        MoveTelescopeFocus.execute({'tcs_cfg_focus': 1.0})

     DESCRIPTION
        With the 'print_only' argument, show the current position of the
        telescope secondary.  With 'tel_foc_x' argument, reset the
        telescope secondary to the given value.

     DICTIONARY KEY
        tel_foc_x = new value for telescope secondary position
        print_only = True
            to print the current telescope focus value
     KTL SERVICE & KEYWORDS
         dcs: telfocus, secmove

    adapted from sh script: kss/mosfire/scripts/procs/tel/telfoc

    """

    @classmethod
    def add_cmdline_args(cls, parser, cfg=None):
        """
        The arguments to add to the command line interface.

        :param parser: <ArgumentParser>
            the instance of the parser to add the arguments to .
        :param cfg: <class 'configparser.ConfigParser'> the config file parser.

        :return: <ArgumentParser>
        """
        # read the config file
        cfg = cls._load_config(cls, cfg)

        # add the command line description
        parser.description = f'Set/show the telescope secondary position.' \
                             f'Modifies DCS KTL keywords: TELFOCUS, SECMOVE.'


        cls.key_tel_focus = cls._cfg_val(cfg, 'ob_keys', 'tel_foc')

        parser = cls._add_inst_arg(cls, parser, cfg)

        args_to_add = OrderedDict([
            (cls.key_tel_focus, {'type': float,
                                 'help': 'The new value for telescope '
                                         'secondary position.'})
        ])
        parser = cls._add_args(parser, args_to_add, print_only=True)

        return super().add_cmdline_args(parser, cfg)

    @classmethod
    def pre_condition(cls, args, logger, cfg):
        """
        :param args:  <dict> The OB (or subset) in dictionary form
        :param logger: <DDOILoggerClient>, optional
            The DDOILoggerClient that should be used. If none is provided,
            defaults to a generic name specified in the config, by default None
        :param cfg: <class 'configparser.ConfigParser'> the config file parser.
        """

    @classmethod
    def perform(cls, args, logger, cfg):
        """
        :param args:  <dict> The OB (or subset) in dictionary form
        :param logger: <DDOILoggerClient>, optional
            The DDOILoggerClient that should be used. If none is provided,
            defaults to a generic name specified in the config, by default None
        :param cfg: <class 'configparser.ConfigParser'> the config file parser.

        :return: None
        """

        # check if it is only set to print the current values
        cls.print_only = args.get('print_only', False)

        if cls.print_only:
            current_focus = ktl.read('dcs', 'telfocus')
            msg = f"Current Focus = {current_focus}"
            cls.write_msg(logger, msg, print_only=True)

            return

        if not hasattr(cls, 'key_tel_focus'):
            cls.key_tel_focus = cls._cfg_val(cfg, 'ob_keys', 'tel_foc')

        focus_move_val = cls._get_arg_value(args, cls.key_tel_focus)

        timeout = int(cls._cfg_val(cfg, 'ktl_timeout', 'default'))

        # the ktl key name to modify and the value
        key_val = {
            'telfocus': focus_move_val,
            'secmove': 1,
        }
        cls._write_to_kw(cls, cfg, 'dcs', key_val, logger, cls.__name__)

        try:
            ktl.waitfor('secmove=0', service='dcs', timeout=timeout)
        except ktl.TimeoutException:
            msg = f'{cls.__name__} timeout for secondary move.'
            if logger:
                logger.error(msg)
            raise DDOIKTLTimeOut(msg)


    @classmethod
    def post_condition(cls, args, logger, cfg):
        """
        :param args:  <dict> The OB (or subset) in dictionary form
        :param logger: <DDOILoggerClient>, optional
            The DDOILoggerClient that should be used. If none is provided,
            defaults to a generic name specified in the config, by default None
        :param cfg: <class 'configparser.ConfigParser'> the config file parser.

        :return: None
        """
        return
