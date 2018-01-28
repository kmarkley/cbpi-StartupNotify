# -*- coding: utf-8 -*-
################################################################################

from modules import cbpi

################################################################################
@cbpi.initalizer(order=9999)
def init(cbpi):

    equipment = []
    for key, fermenter in cbpi.cache.get("fermenter").iteritems():
        # for fermenters that share actors, only set the first to auto
        if (fermenter.heater not in equipment) and (fermenter.cooler not in equipment):
            if fermenter.heater:
                equipment.append(fermenter.heater)
            if fermenter.cooler:
                equipment.append(fermenter.cooler)
            # restart controller if stopped
            if (fermenter.state is False) and (fermenter.logic):
                cbpi.app.logger.info("StartupNotify: restarting auto mode for '{}'".format(fermenter.name))
                cfg = fermenter.config.copy()
                cfg.update(dict(api=cbpi, fermenter_id=fermenter.id, heater=fermenter.heater, sensor=fermenter.sensor))
                instance = cbpi.get_fermentation_controller(fermenter.logic).get("class")(**cfg)
                instance.init()
                fermenter.instance = instance
                def run(instance):
                    instance.run()
                t = cbpi.socketio.start_background_task(target=run, instance=instance)
                fermenter.state = True
                cbpi.emit("UPDATE_FERMENTER", cbpi.cache.get("fermenter")[key])

    headline = "Startup Detected"
    message = "Fermenters set to auto.\nYou may need to check your brews!"
    cbpi.notify(headline, message, type="danger", timeout=10000)
