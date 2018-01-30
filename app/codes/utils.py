# -*- coding: utf-8 -*-
import os
import pandas as pd
import numpy as np
import operator
from functools import reduce
from collections import OrderedDict, deque
from itertools import zip_longest



def read_bom_file(path):
    """
    read the entire dataset and return it

    args :
        path : path to the dataset
    return :
        dataset : component data
        operation_data : data about the operations
        base_material : base materials data
    """
    try:
        dataset = pd.read_excel(io=path)
        dataset = dataset.rename({"Numéro d'article" : 'components',
                                  "Composant nomenclature": 'sub_components'}, axis=1)
        components_data = dataset[['Description composant nomenclature',
                                   'Taux rebut composant',
                                   'Fixé',
                                   'components',
                                   'sub_components',
                                   'Version de production',
                                   'Quantité de base opération',
                                   'Quantité du composant',
                                   'Unité de mesure du composant',
                                   'Quantité de base Nomenclature',
                                   'Unité de mesure pour Qté de base opérati']]
        components_data = components_data.assign(
            Fixe=components_data['Fixé'].apply(lambda x: True if x == 'X' else False),
            taux=components_data['Taux rebut composant'].fillna(1).apply(lambda x: 1+x/100 if x != 1 else x))
        operation_data = dataset[['Resource',
                                  'Quantité de base opération',
                                  'components',
                                  'Valeur standard 1 (tps prep)',
                                  'Valeur standard 2 (tps MO directe-Fixe)',
                                  'Valeur standard 2 (tps MO directe-Var)',
                                  'Valeur standard 4(tps Mach/Ordo-Fixe)',
                                  'Valeur standard 5 (tps Mach/Ordo-Var)',
                                  'Valeur standard - (tps indirect)',
                                  'Texte court opération',
                                  'Numéro d\'opération']]
        operation_data = operation_data.rename(
            {'Valeur standard 1 (tps prep)':'preparation',
             'Valeur standard 2 (tps MO directe-Fixe)': 'labour_fixes',
             'Valeur standard 2 (tps MO directe-Var)':'labour_variable',
             'Valeur standard 4(tps Mach/Ordo-Fixe)':'machine_fixe',
             'Valeur standard 5 (tps Mach/Ordo-Var)': 'machine_variable',
             'Valeur standard - (tps indirect)':'temps_indirect',
             'Numéro d\'opération' : 'operation_number',
             'Texte court opération':'operation_name'}, axis=1)
        operation_data = operation_data.assign(
            machine_price=np.ones(shape=operation_data.operation_name.shape))
        operation_data = operation_data.dropna(axis=0)
        operation_data.set_index('components', inplace=True)
        base_material = components_data.sub_components.loc[~components_data.sub_components.isin(components_data.components)]
        components_with_sub = dataset.sub_components[dataset.sub_components.isin(dataset.components)]
        return components_data, operation_data, base_material, components_with_sub
    except Exception as e:
        raise e


def get_sub_component(product, components_data):
    """
    this function will return sub-components of components
    """
    return components_data.loc[components_data.components==product].get('sub_components').dropna().values

def get_sub_component_base_quatities(product, components_data):
    """
    the following  function will return sub-components and their quantity for a given product
    """
    data_set = components_data.loc[components_data.components==product][['sub_components', 'Quantité du composant']].dropna()
    return dict(zip(data_set['sub_components'], data_set['Quantité du composant']))

def build_tree(x, components_data):
    """
    the function takes a product as an argument and return his bill of material as a tree structure
    the bom is blazed
    """
    if get_sub_component(x, components_data).size != 0:
        return {x: [build_tree(v, components_data) for v in get_sub_component(x, components_data)]}
    else:
        return x

def get_bom(product, components_data):
    """ using the BFS algorithm to get the multi level BOM """
    tree = build_tree(product, components_data)
    results = []
    queue = deque([(tree, 1)])
    while queue:
        x, level = queue.popleft()
        if isinstance(x, dict):
            parent, children = list(x.items())[0]
            results.append({parent: get_sub_component_base_quatities(parent, components_data), 'level':level})
            for child in children:
                queue.append((child, level+1))
    return results


def build_bom(results, batch_size, components_data, base_material, folder):
    """
    build the bill of material from the results for a given component
    """
    final_result = []
    root_product = list(results[0].keys())[0]
    batch_size = batch_size
    required_quantity_dict = {root_product: batch_size}
    for index, component in enumerate(results):
        level = results[index]['level']
        for name, sub_component in component.items():
            if name not in  ['required_quantity', 'level']:
                sub_base = components_data[['Quantité de base Nomenclature', 'Unité de mesure pour Qté de base opérati']].loc[components_data.components == name].values[0]
                sub_base_quantity = float(sub_base[0])
                sub_required_quantity = required_quantity_dict.get(name, sub_base_quantity)
                for item, quantity in sub_component.items():
                    element_dict = {}
                    infos = components_data[['Unité de mesure du composant',
                                             'Description composant nomenclature',
                                             'Fixe',
                                             'taux']]
                    infos = infos.loc[operator.and_(components_data.sub_components == item, components_data.components == name)].values[0]
                    sub_unit = infos[0]
                    sub_name = infos[1]
                    fixed = infos[2]
                    taux = infos[3]
                    if sub_unit in ['PCY', '/PC']:
                        if not fixed :
                            new_quantity = np.ceil((np.ceil(quantity )* sub_required_quantity * taux ) / sub_base_quantity)
                        else :
                            new_quantity = np.ceil(quantity *taux )
                    else:
                        if not fixed:
                            new_quantity = (quantity * sub_required_quantity * taux) / sub_base_quantity
                        else:
                            new_quantity = quantity * taux
                    results[index][name][item] = new_quantity
                    element_dict['item'] = item
                    element_dict['level'] = level
                    element_dict['quantity'] = new_quantity
                    element_dict['unit'] = sub_unit
                    element_dict['name'] = sub_name
                    if item not in base_material.values:
                        required_quantity_dict[item] = new_quantity
                    final_result.append(element_dict)
        results[index]['required_quantity'] = sub_required_quantity
    output_df = pd.DataFrame(final_result)
    output_df.to_csv(path_or_buf= os.path.join(folder, "BOM{}_{}.csv".format(root_product, batch_size)))
    return output_df


def read_ressources_data(path):
    """
    this function given ressources data it should read it
    """

    try:
        ressources_data = pd.read_excel(io=path)
        ressources_data.set_index("Poste de travail", inplace=True)
        ressources_data = ressources_data.loc[:, ressources_data.columns[15:25]]
        #getting the only ressources we will need
        ressources_data.rename(
            {"Heure":'start',
             "Heure.1": "end",
             "Heure.2":"pause"}, axis=1, inplace=True)
        ressources_data = ressources_data.assign(
            start=pd.to_datetime(ressources_data['start'],
                                 format='%H:%M:%S').dt.time.apply(lambda x: (x.hour + x.minute/60)),
            end=pd.to_datetime(ressources_data['end'],
                               format='%H:%M:%S').dt.time.apply(lambda x: (x.hour + x.minute/60)),
            pause=pd.to_datetime(ressources_data['pause'],
                                 format='%H:%M:%S').dt.time.apply(lambda x: (x.hour + x.minute/60)))
        ressources_data = ressources_data.assign(
            hours_days=(ressources_data.end - ressources_data.start - ressources_data.pause)* ressources_data['%'])
        return ressources_data
    except Exception as e:
        raise e



def read_inter_operartions(path):
    """
    this function given interoperation data it should read it
    """

    try:
        inter_operation_time = pd.read_excel(io=path)
        inter_operation_time = inter_operation_time.assign(
            curent_op=inter_operation_time['Task list node']*10,
            next_op=inter_operation_time['Task list node.1']*10,
            deleted=inter_operation_time['Deletion indicator'].apply(lambda x: True if x == 'X' else False))
        inter_operation_time.fillna(value={'Relationship unit':'D'}, inplace=True)
        inter_operation_time.rename({'Relationship type':'Type de liaison',
                                     'curent_op': 'Phase prédécesserice',
                                     'next_op': 'Phase successive',
                                     'Offset rel.ship' : 'delay',
                                     'Relationship unit': 'Unité de mesure décallage'}, axis=1, inplace=True)
        inter_operation_time.set_index('Material', inplace=True)
        return inter_operation_time
    except Exception as e:
        raise e


def get_operation_sequence(name, inter_operation_time):
    """
    given an item this will return his operation sequences


    """
    current_op = 20
    df_inter = inter_operation_time.loc[[name]].reset_index()
    position = 0
    operations = [[[20]]]
    delays = []
    for i in range(len(df_inter) ):
        sub_inter_df = df_inter[position:]
        links_infos = sub_inter_df.loc[sub_inter_df['Phase prédécesserice'] == current_op]
        links_infos = links_infos[['Phase successive',
                                   'Type de liaison',
                                   'delay',
                                   'Unité de mesure décallage',
                                   'deleted']].head(1)
        if not links_infos.empty:
            position = links_infos.index[0] +1
            #print(position)
            next_op = links_infos['Phase successive'].values[0]
            delay = links_infos['delay'].values[0]
            unit = links_infos['Unité de mesure décallage'].values[0]
            link_type = links_infos['Type de liaison'].values[0]
            deleted = links_infos['deleted'].values[0]
            if link_type == 'SS':
                operations[-1].extend([[current_op, next_op]]) #to the last one

            else:
                operations.append([[current_op], [next_op]])
            if not deleted:
                delays.append((delay, unit)) #need to be improved
            current_op = next_op
    operations = [op[-1]  for op in operations]
    #need to consider only the last operation in the operation list
    operations = reduce(operator.concat, operations)
    return zip_longest(operations, delays)





def build_boo(product, level, required_quantity, operation_data, component_with_interoperation, inter_operation_time):
    """
    """
    machine_variable = machine_fixed = temp_indirect = preparation = delays = 0
    df = operation_data.loc[[product],['hours_days',
                                       'Quantité de base opération',
                                       'operation_number',
                                       'operation_name',
                                       'preparation',
                                       'labour_fixes',
                                       'labour_variable',
                                       'machine_fixe',
                                       'machine_variable',
                                       'temps_indirect'],
                                      ].sort_values('operation_number').drop_duplicates('operation_number',)
    if product in component_with_interoperation:
        for oper, delay in get_operation_sequence(product, inter_operation_time):
            sub_df = df.loc[df.operation_number == oper]
            if not sub_df.empty:
                machine_variable += ((sub_df.machine_variable / sub_df.hours_days)  * required_quantity / sub_df.get('Quantité de base opération')).fillna(0).iloc[0]
                machine_fixed += (sub_df.machine_fixe / sub_df.hours_days).fillna(0).iloc[0]
                temp_indirect += sub_df.temps_indirect.fillna(0).iloc[0]
                preparation += sub_df.preparation.fillna(0).iloc[0]
                if delay:
                    if delay[1] != 'D':
                        delays += (delay[0] / sub_df.hours_days.iloc[0])
                    else:
                        delays += delay[0]
                else:
                    delays += 0
    else:
        machine_variable += ((df.machine_variable / df.hours_days)  * required_quantity / df.get('Quantité de base opération')).fillna(0).iloc[0]
        machine_fixed += (df.machine_fixe / df.hours_days).fillna(0).iloc[0]
        temp_indirect += df.temps_indirect.fillna(0).iloc[0]
        preparation += df.preparation.fillna(0).iloc[0]
    total_time = machine_fixed + machine_variable
    new_df = pd.DataFrame({'level' : [level],
                           'days' : [total_time],
                           'component' : [product],
                           'preparation':[preparation],
                           'temps_indirect': [temp_indirect],
                           'delay': [delays]},)
    return new_df.fillna(0)




def get_max_time(results, excluded_products, operation_data, component_with_interoperation, inter_operation_time, folder):
    """
    get maximun time to produce a product
    args:
    results : results for BOM  explosion of a given product
    return : the sum  of production time
    """
    boo_df = pd.DataFrame()
    root_product = list(results[0].keys())[0]
    for item in results:
        name = list(item.keys())[0]
        level = item['level']
        required_quantity = item['required_quantity']
        if not name in excluded_products.index:
            boo_df = boo_df.append(
                build_boo(
                    name,
                    level,
                    required_quantity,
                    operation_data,
                    component_with_interoperation,
                    inter_operation_time))
    if not boo_df.empty:
        boo_df = boo_df.assign(total_days=boo_df.delay + boo_df.days)
        boo_df.to_csv(path_or_buf=os.path.join(folder, "BOO_{}.csv".format(root_product)))
        #this will return the maximun hours per level of a given product
        hours_df = boo_df[['total_days', 'component', 'level']]
        hours_df = hours_df.sort_values(['total_days', 'component'],
                                        ascending=[False, True]).groupby('level').first()
    hours_df.to_csv(path_or_buf=os.path.join(folder, "hours_{}.csv".format(root_product)))
    hours_df.reset_index(inplace=True)
    hours_df_flatten = hours_df.stack().to_frame().T
    hours_df_flatten = hours_df_flatten.assign(TOTAl_DAYS=np.sum(hours_df.total_days))
    hours_df_flatten.index = [root_product]
    return hours_df_flatten, boo_df



def read_excluded_product(path):
    """
    read excluded product list at specified path
    args :
    path : path of specified product
    return : a series of ecluded product
    """
    try:
        excluded_products = pd.read_excel(io=path, sheet_name=1, header=None, squeeze=True)
        return excluded_products
    except Exception as e:
        raise e



def read_product(path):
    """
    read list of product for mass claculations
    args :
        path : path for the file
    return : a dtaframe with all files as index
    """
    try:
        products = pd.read_excel(io=path, sheet_name=0)
        products.set_index('SKU', inplace=True)
        return products
    except Exception as e:
        raise e
