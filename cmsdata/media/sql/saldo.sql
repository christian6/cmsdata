/*create or replace view home_construct
as
select d.entry_id as doc,h.transfer, d.materials_id, d.quantity,d.price,'ENTRY' AS type from home_documentin h inner join home_detdocumentin d on h.entry_id LIKE d.entry_id
union all
select d.output_id as doc,h.transfer, d.materials_id, d.quantity,d.price,'OUTPUT' as type from home_documentout h inner join home_detdocumentout d on h.output_id LIKE d.output_id
*/
create or replace function sp_constructinventory()
returns bool as
$$
DECLARE
  salstar double precision;
  salactual double precision;
  priactual double precision;
  x record;
  counter integer;
  months character(2);
  years character(4);
begin
salactual := 0;
priactual := 0;
counter := 0;
  if (select count(period) from home_inventory where materials_id like '220018030014003')::INTEGER = 0 then
    -- When material no content history
    for x in select *, (select COUNT(*) from home_construct where materials_id like '220018030014003') as co from home_construct where materials_id like '220018030014003' group by doc,transfer,materials_id,quantity, price, type order by transfer asc loop
      if months NOT LIKE to_char(x.transfer, 'MM') and months is not null then
        raise notice 'dentro de moths  % %',months, to_char(x.transfer, 'MM');
        if counter >= 0 then
          --raise notice 'saldos % %',salactual, priactual;
          insert into home_inventory(period,register,month,materials_id,quantity,price,exists) values(years,now()::date,months,x.materials_id,salactual,priactual,True);
        end if;
      else
        raise notice 'son iguales';
      end if;
      -- compare if is entry or output
      --raise notice ' saldo: %',salactual;
      if x.type LIKE 'ENTRY' then
        salactual:= (salactual + x.quantity);
      else
       salactual:= (salactual - x.quantity);
      end if;
      raise notice ' saldo: %',salactual;
      priactual:= x.price;
      counter:= counter + 1;
      months := to_char(x.transfer, 'MM');
      years := to_char(x.transfer, 'YYYY');
      if x.co = counter then
          insert into home_inventory(period,register,month,materials_id,quantity,price,exists) values(years,now()::date,months,x.materials_id,salactual,priactual,True);
      end if;
      -- RAISE NOTICE '%',x.transfer;
    end loop;
    --raise info 'saldo final: %',salactual;
  end if;
  --for x in select 
return true;
exception when others then
return false;
  raise notice 'The transaction is in an uncommittable state. '
               'Transaction was rolled back';
  raise notice '% %', SQLERRM, SQLSTATE;
end;
$$
language plpgsql;

select * from home_construct where materials_id like '220018030014003'
delete from home_inventory
select * from home_inventory
select * from home_detdocumentin where materials_id like '220018030014003'
select * from sp_constructinventory()
"2013";"2014-06-24";"01";"220018030014003";6;30
"2013";"2014-06-24";"02";"220018030014003";22;20
"2013";"2014-06-24";"03";"220018030014003";82;8.9
"2013";"2014-06-24";"04";"220018030014003";95;9
"2013";"2014-06-24";"08";"220018030014003";141;13
"2013";"2014-06-24";"11";"220018030014003";167;11
