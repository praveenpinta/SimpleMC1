def write_baseConfigGUI(chainsdir, model, analyzername, datasets, general_settings, sampler_settings):
    with open('baseConfigGUI.ini', 'w') as config_file:
        config_file.write('[custom]\n')
        config_file.write('chainsdir = {}\n'.format(chainsdir))
        config_file.write('model = {}\n'.format(model))
        if general_settings[0] == False:
            config_file.write('prefact = phy\n')
        else:
            config_file.write('prefact = pre\n')
        config_file.write('varys8 = {}\n'.format(general_settings[1]))
        config_file.write('datasets = {}\n'.format(datasets))
        config_file.write('analyzername = {}\n'.format(analyzername))
        config_file.write('addDerived = {}\n'.format(general_settings[3]))
        config_file.write('mcevidence = {}\n'.format(sampler_settings[6]))
        config_file.write('mcevidence_k = {}\n'.format(sampler_settings[7]))
        config_file.write('overwrite = {}\n'.format(general_settings[2]))
        config_file.write('getdist = {}\n'.format(sampler_settings[8]))
        config_file.write('corner = {}\n'.format(sampler_settings[9]))
        config_file.write('simpleplot = {}\n'.format(sampler_settings[10]))
        config_file.write('showfig = {}\n'.format(sampler_settings[11]))
        config_file.write('[mcmc]\n')
        config_file.write('nsamp = {}\n'.format(sampler_settings[0]))
        config_file.write('skip = {}\n'.format(sampler_settings[1]))
        config_file.write('temp = {}\n'.format(sampler_settings[2]))
        config_file.write('GRstop = {}\n'.format(sampler_settings[3]))
        config_file.write('checkGR = {}\n'.format(sampler_settings[4]))
        config_file.write('chainno = {}\n'.format(sampler_settings[5]))
    config_file.close()