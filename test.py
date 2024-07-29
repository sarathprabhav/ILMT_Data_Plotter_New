names = "utstart,ra,dec,ra1,dec1,ra2,dec2,dec_obs,ra_obs,psf_a,psf_b,psf_pa,zeropt,poserr,raerr,decerr,zperr,magerr,fwhm,sky,param2,param7,param48,param49"
name_list = names.split(",")
print(name_list)

parameter_dict ={}
for name in name_list:
    print('\n')
    parameter_dict[name] = input(f"{name}---?")
    
print(parameter_dict)
