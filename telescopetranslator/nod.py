from ddoitranslatormodule.ddoiexceptions.DDOIExceptions import DDOIPreConditionNotRun
from telescopetranslator.BaseTelescope import TelescopeBase

import ktl
from collections import OrderedDict


class SetNodValues(TelescopeBase):
    """
    nod - set nod parameters

    SYNOPSIS
        SetNodValues.execute({
            'tcs_offset_east': float,
            'tcs_offset_north': float,
            'instrument': str of instrument name
            })

    RUN
        from ddoi_telescope_translator import nod
        nod.SetNodValues.execute({'tcs_offset_north': 10.0,
                                  'tcs_offset_east': 5.0,
                                   'instrument': 'KPF'})

    DESCRIPTION
        sets the telescope nod parameters to dE arcsec East
             and dN arcsec North

    ARGUMENTS

    OPTIONS

    EXAMPLES
        1) Show current nod params:
            SetNodValues.execute({'print_only': True})


        1) Set east nod to 5 and north nod to 10:
            SetNodValues.execute({'tcs_offset_north': 10.0,
                                  'tcs_offset_east': 5.0,
                                  'instrument': INST}})

    KTL SERVICE & KEYWORDS
       servers: instrument
        keywords: node nodn

    adapted from sh script: kss/mosfire/scripts/procs/tel/
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
        parser.description = f'Set the nod parameters.  Modifies Instrument ' \
                             f'Specific parameters for nodding North and East.'


        cls.key_nod_north = cls._cfg_val(cfg, 'ob_keys', 'tel_north_offset').upper()
        cls.key_nod_east = cls._cfg_val(cfg, 'ob_keys', 'tel_east_offset').upper()

        parser = cls._add_inst_arg(cls, parser, cfg)

        args_to_add = OrderedDict([
            (cls.key_nod_north, {
                'type': float,
                'help': 'Set the North Nod value [arcseconds]'
            }),
            (cls.key_nod_east, {
                'type': float,
                'help': 'Set the East Nod value [arcseconds]'
            })
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

        :return: bool
        """
        cls.inst = cls.get_inst_name(cls, args, cfg)

        # check if it is only set to print the current values
        cls.print_only = args.get('print_only', False)

        if cls.print_only:
            return True

        if not hasattr(cls, 'key_nod_north'):
            cls.key_nod_north = cls._cfg_val(cfg, 'ob_keys',
                                                  'tel_north_offset')
        if not hasattr(cls, 'key_nod_east'):
            cls.key_nod_east = cls._cfg_val(cfg, 'ob_keys',
                                                 'tel_east_offset')

        cls.nod_north = cls._get_arg_value(args, cls.key_nod_north)
        cls.nod_east = cls._get_arg_value(args, cls.key_nod_east)
        
        return True

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
        if not hasattr(cls, 'print_only'):
            raise DDOIPreConditionNotRun(cls.__name__)

        serv_name = cls._cfg_val(cfg, 'ktl_serv', cls.inst)

        if cls.print_only:
            key_nod_north = cls._cfg_val(cfg, f'ktl_kw_{cls.inst}',
                                              'nod_north')
            key_nod_east = cls._cfg_val(cfg, f'ktl_kw_{cls.inst}',
                                             'nod_east')

            msg = f"Current Nod Values N: {ktl.read(serv_name, key_nod_north)}" \
                  f", E: {ktl.read(serv_name, key_nod_east)}"
            cls.write_msg(logger, msg, print_only=True)

            return

        # write to instrument keywords,  keys are cfg keys not ktl keys
        key_val = {
            'nod_north': cls.nod_north,
            'nod_east': cls.nod_east
        }
        cls._write_to_kw(cls, cfg, serv_name, key_val, logger,
                         cls.__name__, cfg_key=True)

        msg = f"New Nod Values N: {cls.nod_north}. E: {cls.nod_east}"
        cls.write_msg(logger, msg)

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