<?php
/*
 * bencoding
 * This class is for encoding php types to the bencode syntax and
 * decoding a bencode string to php types. You need this if you
 * want to create/read a torrent file. For more informations about
 * bencode goto: http://bittorrent.org/beps/bep_0003.html
 * I have developed this class for my framework psx <http://phpsx.org>
 * but you can also use this outside.
 *
 * Copyright (c) 2009 Christoph Kappestein <hide@address.com>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 * @author  Christoph Kappestein <hide@address.com>
 * @license http://www.gnu.org/licenses/gpl.html GPLv3
 * @link    http://phpsx.org
 */


/**
 * bencoding_exception
 *
 */
class bencoding_exception extends exception
{
}

/**
 * bencoding
 *
 */
class bencoding
{
	/**
	 * Encode $value to the bencode syntax
	 *
	 * @access public
	 * @param  mixed $value 
	 * @return string
	 */
	public function encode($value)
	{
		$type = gettype($value);
		$out  = '';

		switch($type)
		{
			case 'integer':

				$out.= 'i' . $value . 'e';

				break;

			case 'string':

				$out.= strlen($value) . ':' . utf8_encode($value);

				break;

			case 'array':

				if(!$this->is_associative($value))
				{
					$out.= 'l';
					foreach($value as $entry)
					{
						$out.= $this->encode($entry);
					}

					$out.= 'e';
				}
				else
				{
					$out.= 'd';
					ksort($value);
					foreach($value as $key => $entry)
					{
						$out.= $this->encode($key) . $this->encode($entry);
					}

					$out.= 'e';
				}

				break;

			default:
				throw new bencoding_exception('type must be integer / string or array');
				break;
		}

		return $out;
	}

	/**
	 * Decode $value to php types
	 *
	 * @access public
	 * @param  string $value 
	 * @return integer|string|array
	 */
	public function decode($value)
	{
		list($v, $r) = $this->rec_decode($value);

		return $v;
	}

	private function rec_decode($value)
	{
		switch($value[0])
		{
			# list
			case 'l':

				$value = substr($value, 1, -1);
				$out   = array();

				while(!empty($value))
				{
					list($v, $r) = $this->rec_decode($value);

					$value = $r;

					if(!empty($v))
					{
						$out[] = $v;
					}
				}

				return array($out, false);

				break;

			# dictonary
			case 'd':

				$value = substr($value, 1, -1);
				$out   = array();

				while(!empty($value))
				{
					list($k, $r) = $this->rec_decode($value);

					$value = $r;

					list($v, $r) = $this->rec_decode($value);

					$value = $r;

					if(!empty($k) && !empty($v))
					{
						$out[$k] = $v;
					}
				}

				return array($out, false);

				break;

			# integer
			case 'i':

				return $this->decode_int($value);

				break;

			# string
			case '0':
			case '1':
			case '2':
			case '3':
			case '4':
			case '5':
			case '6':
			case '7':
			case '8':
			case '9':

				return $this->decode_str($value);

				break;

			default:

				return false;
		}
	}

	private function decode_int($value)
	{
		if(isset($value[0]) && $value[0] == 'i')
		{
			$i      = 1;
			$length = '';

			while($value[$i] != 'e')
			{
				$length.= $value[$i];

				$i++;
			}

			$result = intval($length);
			$value  = substr($value, strlen($length) + 2);

			return array($result, $value);
		}

		return array(false, false);
	}

	private function decode_str($value)
	{
		if(is_numeric($value[0]))
		{
			$i      = 0;
			$length = '';

			while($value[$i] != ':')
			{
				$length.= $value[$i];

				$i++;
			}

			$length = intval($length);
			$result = substr($value, $i + 1, $length);
			$value  = substr($value, strlen($length) + 1 + $length);

			return array($result, $value);
		}

		return array(false, false);
	}

	private function is_associative($array)
	{
		for($i = 0; $i < count($array); $i++)
		{
			if(!isset($array[$i]))
			{
				return true;
			}
		}

		return false;
	}
}
?>
