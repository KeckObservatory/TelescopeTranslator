from ddoitranslatormodule.BaseFunction import TranslatorModuleFunction
from ddoitranslatormodule.DDOIExceptions import DDOIPreConditionNotRun

import tel_utils as utils

import ktl


class SetNodEastValue(TranslatorModuleFunction):
    """
    node - set nod parameters for east motions

    SYNOPSIS
        SetNodEastValue.execute({'tel_east_offset': float,
                                 'inst': str of instrument name})

    DESCRIPTION
        sets the telescope nod parameters to dE arcsec East

    ARGUMENTS

    OPTIONS

    EXAMPLES
        1) Set east nod to 5 :
            SetNodValues.execute({'tel_east_offset': 5.0})

        2) Show current nod params:
            SetNodValues.execute()

    ENVIRONMENT VARIABLES

    FILES

    SERVERS & KEYWORDS
       servers: instrument
        keywords: node nodn

    KTL SERVICE & KEYWORDS

    adapted from sh script: kss/mosfire/scripts/procs/tel/
    """

    @classmethod
    def pre_condition(cls, args, logger, cfg):
        """
        :param args:  <dict> The OB (or subset) in dictionary form
        :param logger: <DDOILoggerClient>, optional
            The DDOILoggerClient that should be used. If none is provided,
            defaults to a generic name specified in the config, by default None
        :param cfg: <str> filepath, optional
            File path to the config that should be used, by default None

        :return: bool
        """
        cls.inst = utils.get_inst_name(args, cls.__name__)

        # check if it is only set to print the current values
        cls.print_only = utils.print_only(args, cfg, 'tel_keys', ['tel_east_offset'])

        if cls.print_only:
            return True

        key_nod_east = utils.config_param(cfg, 'ob_keys', 'tel_east_offset')
        cls.nod_east = utils.check_float(args, key_nod_east, logger)
        
        return True

    @classmethod
    def perform(cls, args, logger, cfg):
        """
        :param args:  <dict> The OB (or subset) in dictionary form
        :param logger: <DDOILoggerClient>, optional
            The DDOILoggerClient that should be used. If none is provided,
            defaults to a generic name specified in the config, by default None
        :param cfg: <str> filepath, optional
            File path to the config that should be used, by default None

        :return: None
        """
        if not hasattr(cls, 'print_only'):
            raise DDOIPreConditionNotRun(cls.__name__)

        serv_name = utils.config_param(cfg, 'ktl_serv', cls.inst)

        if cls.print_only:
            key_nod_east = utils.config_param(cfg, f'ktl_kw_{cls.inst}', 'nod_east')

            msg = f"Current Nod Values E: {ktl.read(serv_name, key_nod_east)}"
            utils.write_msg(logger, msg)
            return

        key_val = {'nod_east': cls.nod_east}
        utils.write_to_kw(cfg, serv_name, key_val, logger, cls.__name__)

        msg = f"New Nod East Value: {cls.nod_east}"
        utils.write_msg(logger, msg)

    @classmethod
    def post_condition(cls, args, logger, cfg):
        """
        :param args:  <dict> The OB (or subset) in dictionary form
        :param logger: <DDOILoggerClient>, optional
            The DDOILoggerClient that should be used. If none is provided,
            defaults to a generic name specified in the config, by default None
        :param cfg: <str> filepath, optional
            File path to the config that should be used, by default None

        :return: None
        """
        return


