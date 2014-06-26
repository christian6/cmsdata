select * from home_construct
/* consult view construct a material with period and month */
create or replace function spconsultbymaterialperiodmonth_inventory(character varying, character varying, character varying)
returns setof home_construct as
$$
select c.doc,c.transfer,c.materials_id,c.quantity,c.price,c.type from home_construct c where c.materials_id like $1 and to_char(c.transfer, 'YYYY') like $2 and to_char(c.transfer, 'MM') like $3 order by c.transfer asc;
$$
language sql;
/* consult view construct u material with period */
create or replace function spconsultbymaterialperiod_inventory(character varying, character varying)
returns setof home_construct as
$$
select c.doc,c.transfer,c.materials_id,c.quantity,c.price,c.type from home_construct c where c.materials_id like $1 and to_char(c.transfer, 'YYYY') like $2 order by c.transfer asc;
$$
language sql;
select * from spconsultbymaterialperiodmonth_inventory('220018030014001','2013','01');
select * from spconsultbymaterialperiod_inventory('220018030014001','2013');