#!/usr/bin/python
# -*- coding: utf-8 -*-
from datetime import datetime
from iso8601 import parse_date
import pytz
import urllib
import re
import os


tz = str(datetime.now(pytz.timezone('Europe/Kiev')))[26:]


def prepare_tender_data_asset(tender_data):
    tender_data['data']['assetCustodian']['identifier']['id'] = u'01010122'
    tender_data['data']['assetCustodian']['name'] = u'ТОВ Орган Приватизации'
    tender_data['data']['assetCustodian']['identifier']['legalName'] = u'ТОВ Орган Приватизации'
    tender_data['data']['assetCustodian']['contactPoint']['name'] = u'Гоголь Микола Васильович'
    tender_data['data']['assetCustodian']['contactPoint']['telephone'] = u'+38(101)010-10-10'
    tender_data['data']['assetCustodian']['contactPoint']['email'] = u'testprozorroyowner@gmail.com'
    for item in range(len(tender_data['data']['items'])):
        if tender_data['data']['items'][item]['address']['region'] == u'місто Київ':
            tender_data['data']['items'][item]['address']['region'] = u'Київ'
    return tender_data


def prepare_tender_data(role, data):
    if role == 'tender_owner' and 'assetCustodian' in data['data']:
        data = prepare_tender_data_asset(data)
    return data


def convert_date_from_item(date):
    date = datetime.strptime(date, '%d/%m/%Y %H:%M:%S').strftime('%Y-%m-%d')
    return '{}T00:00:00{}'.format(date, tz)


def convert_date(date):
    if '.' in date:
        date = datetime.strptime(date, '%d.%m.%Y %H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S.%f')
    else:
        date = datetime.strptime(date, '%d/%m/%Y %H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S.%f')
    return '{}{}'.format(date, tz)


def convert_date_for_item(date):
    date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S{}'.format(tz)).strftime('%d/%m/%Y %H:%M')
    return '{}'.format(date)


def convert_date_for_date_paid(date):
    iso_dt = parse_date(date)
    date_string = iso_dt.strftime("%d.%m.%Y %H:%M")
    return date_string


def convert_date_for_auction(date):
    date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%f{}'.format(tz)).strftime('%d/%m/%Y %H:%M:%S')
    return '{}'.format(date)


def convert_date_for_milestone():
    date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S'.format(tz)).strftime('%d.%m.%Y %H:%M')
    return '{}'.format(date)


def convert_date_from_decision(date):
    date = datetime.strptime(date, '%d/%m/%Y'.format(tz)).strftime('%Y-%m-%dT%H:%M:%S.%f')
    return '{}{}'.format(date, tz)


def convert_date_for_decision(date):
    date = datetime.strptime(date, '%Y-%m-%d'.format(tz)).strftime('%d/%m/%Y')
    return '{}'.format(date)


def convert_duration(duration):
    if duration == u'P1M':
        duration = u'P30D'
    days = re.search('\d+D|$', duration).group()
    if len(days) > 0:
        days = days[:-1]
    return days


def adapted_dictionary(value):
    return{
        u'Класифікація згідно CAV': 'CAV',
        u'Класифікація згідно CAV-PS': 'CAV-PS',
        u'Класифікація згідно CPV': 'CPV',
        u'Аукцiон': 'active.auction',
        u'Аукціон': 'active.auction',
        u'Очiкування пропозицiй': 'active.tendering',
        u'Торги не відбулися': 'unsuccessful',
        u'Аукціон не відбувся': 'unsuccessful',
        u'Продаж завершений': 'complete',
        u'Торги скасовано': 'cancelled',
        u'Аукціон відмінено': 'cancelled',
        u'Квалiфiкацiя переможця': 'active.qualification',
        u'Прийняття заяв на участь': 'active.qualification',
        u'Очікується опублікування протоколу': 'active.qualification',
        u'Очікується рішення': 'pending.waiting',
        u'Очікується протокол': 'pending',
        u'Рішення скасоване': 'unsuccessful',
        u'Відмова від очікування': 'cancelled',
        u'Очікується рішення про викуп': 'pending.admission',
        u'Переможець': 'active',
        u'об’єкт реєструється': u'registering',
        u'об’єкт зареєстровано': u'complete',
        u'Об’єкт зареєстровано': u'complete',
        u'Опубліковано': u'pending',
        u'Актив завершено': u'complete',
        u'Публікація інформаційного повідомлення': u'composing',
        u'Перевірка доступності об’єкту': u'verification',
        u'lot.status.pending.deleted': u'pending.deleted',
        u'Об’єкт виключено': u'deleted',
        u'Інформація': u'informationDetails',
        u'об’єктів малої приватизації - аукціон': u'sellout.english',
        u'Заплановано': u'scheduled',
        u'Виконано': u'met',
        u'Не виконано': u'notMet',
        u'Завершений': u'terminated',
        u'Не успішний': u'unsuccessful',
        u'Очікується оплата.': u'active.confirmation',
        u'Очікується оплата': u'active.payment',
        u'Договір оплачено. Очікується наказ': u'active.approval',
        u'Період виконання умов продажу (період оскарження)': u'active',
        u"Приватизація об’єкта завершена.": u'pending.terminated',
        u"Приватизація об’єкта неуспішна.": u'pending.unsuccessful',
        u"Приватизація об’єкта завершена": u'terminated',
        u"Приватизація об’єкта неуспішна": u'unsuccessful'
    }.get(value, value)


def adapt_data(field, value):
    if field == 'tenderAttempts':
        value = int(value)
    elif field == 'value.amount':
        value = float(value)
    elif field == 'minimalStep.amount':
        value = float(value.split(' ')[0])
    elif field == 'guarantee.amount':
        value = float(value.split(' ')[0])
    elif field == 'registrationFee.amount':
        value = float(value.split(' ')[0])
    elif field == 'quantity':
        value = float(value.replace(',', '.'))
    elif field == 'minNumberOfQualifiedBids':
        value = int(value)
    elif 'contractPeriod' in field:
        value = convert_date_from_item(value)
    elif 'tenderPeriod' in field or 'auctionPeriod' in field or 'rectificationPeriod' in field and 'invalidationDate' not in field:
        value = convert_date(value)
    else:
        value = adapted_dictionary(value)
    return value


def adapt_asset_data(field, value):
    if 'date' in field:
        value = convert_date(value)
    elif 'decisionDate' in field:
        value = convert_date_from_decision(value.split(' ')[0])
    elif 'documentType' in field:
        value = adapted_dictionary(value.split(' ')[0])
    elif 'rectificationPeriod.endDate' in field:
        value = convert_date(value)
    elif 'documentType' in field:
        value = value
    else:
        value = adapted_dictionary(value)
    return value


def adapt_lot_data(field, value):
    if 'amount' in field:
        value = float(value.split(' ')[0])
    elif 'tenderingDuration' in field:
        value = value.split(' ')[0]
        if 'M' in value:
            value = 'P{}'.format(value)
        else:
            value = 'P{}D'.format(value)
    elif 'auctionPeriod.startDate' in field:
        value = convert_date(value)
    elif 'classification.id' in field:
        value = value.split(' - ')[0]
    elif 'unit.name' in field:
        value = ' '.join(value.split(' ')[1:])
    elif 'quantity' in field:
        value = float(value.split(' ')[0])
    elif 'registrationFee.amount' in field:
        value = float(value.split(' ')[0])
    elif 'tenderAttempts' in field:
        value = int(value)
    else:
        value = adapted_dictionary(value)
    return value


def adapt_edrpou(value):
    value = str(value)
    if len(value) == 7:
        value += '0'
    return value


def download_file(url, filename, folder):
    urllib.urlretrieve(url, ('{}/{}'.format(folder, filename)))


def get_upload_file_path():
    return os.path.join(os.getcwd(), 'src/robot_tests.broker.uace/Doc.pdf')

