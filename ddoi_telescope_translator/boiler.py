from ddoitranslatormodule.BaseFunction import TranslatorModuleFunction
from ddoitranslatormodule.ddoiexceptions.DDOIExceptions import DDOIPreConditionNotRun

import tel_utils as utils

import ktl


class Boiler(TranslatorModuleFunction):
    """

    KTL SERVICE & KEYWORDS

    adapted from sh script: kss/mosfire/scripts/procs/tel/
    """

    @classmethod
    def add_cmdline_args(cls, parser, cfg):
        """
        The arguments to add to the command line interface.

        :param parser: <ArgumentParser>
            the instance of the parser to add the arguments to .
        :param cfg: <str> filepath, optional
            File path to the config that should be used, by default None

        :return: <ArgumentParser>
        """
        cls.xxx = utils.config_param(cfg, 'ob_keys', '...')

        args_to_add = {
            cls.xxx: {'type': float, 'req': True,
                      'help': 'The offset in Azimuth in degrees.'},
            cls.xxx: {'type': float, 'req': True,
                      'help': 'The offset in Elevation in degrees.'}}
        parser = utils.add_args(parser, args_to_add, print_only=False)

        parser = utils.add_inst_arg(parser)

        return super().add_cmdline_args(parser, cfg)

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
        if not hasattr(cls, '...'):
            cls.xxx = utils.config_param(cfg, 'ob_keys', '...')

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

        cls.serv_name = utils.config_param(cfg, 'ktl_serv', 'dcs')

        key_val = {
            '': ,
            '': ,
            '':
        }
        utils.write_to_kw(cfg, cls.serv_name, key_val, logger, cls.__name__)


        return

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