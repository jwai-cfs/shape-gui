function d = load_json_dict(fn)

fid = fopen(fn); 
raw = fread(fid,inf); 
str = char(raw'); 
fclose(fid); 
d = jsondecode(str);