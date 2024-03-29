from telescopetranslator.BaseTelescope import TelescopeBase

import telescopetranslator.tel_utils as utils

import ktl


class GoToMark(TelescopeBase):
    """
      gomark - restore telescope position to saved offsets

    SYNOPSIS
        GoToMark.execute({'inst': str of instrument name})

    RUN
        from ddoi_telescope_translator import gomark
        gomark.GoToMark({})

    DESCRIPTION
          moves to the position defined by the keywords "raoffset" and
          "decoffset", which are normally loaded by the command "mark".

    KTL SERVICE & KEYWORDS
        server: instrument, dcs
            keywords: raoffset, decoffset, raoff, decoff

    adapted from sh script: kss/mosfire/scripts/procs/tel/gmomark
    """

    @classmethod
    def add_cmdline_args(cls, parser, cfg=None):
        """
        The arguments to add to the command line interface.

        :param parser: <ArgumentParser>
            the instance of the parser to add the arguments to .
        :param config: <class 'configparser.ConfigParser'> the config file parser.

        :return: <ArgumentParser>
        """
        # read the config file
        cfg = cls._load_config(cls, cfg)

        # add the command line description
        parser.description = f'Moves telescope X,Y Instrument Guider ' \
                             f'Coordinates.  Modifies KTL DCS keywords: ' \
                             f'RAOFF, DECOFF, REL2BASE.'

        # add inst parameter as optional
        parser = cls._add_inst_arg(cls, parser, cfg, is_req=False)

        return super().add_cmdline_args(parser, cfg)

    @classmethod
    def pre_condition(cls, args, logger, cfg):
        """
        :param args:  <dict> The OB (or subset) in dictionary form
        :param logger: <DDOILoggerClient>, optional
            The DDOILoggerClient that should be used. If none is provided,
            defaults to a generic name specified in the config, by default None
        :param config: <class 'configparser.ConfigParser'> the config file parser.
        """
    
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
        inst = cls.get_inst_name(cls, args, cfg)

        inst_serv_name = cls._cfg_val(cfg, 'ktl_serv', inst)
        ktl_ra_mark = cls._cfg_val(cfg, f'ktl_kw_{inst}', 'ra_mark')
        ktl_dec_mark = cls._cfg_val(cfg, f'ktl_kw_{inst}', 'dec_mark')

        ra_mark = ktl.read(inst_serv_name, ktl_ra_mark)
        dec_mark = ktl.read(inst_serv_name, ktl_dec_mark)

        # the ktl key name to modify and the value
        key_val = {
            'raoff': ra_mark,
            'decoff': dec_mark,
            'rel2base': 't'
        }
        cls._write_to_kw(cls, cfg, 'dcs', key_val, logger, cls.__name__)


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
        utils.wait_for_cycle(cls, cfg, cls.serv_name, logger)


